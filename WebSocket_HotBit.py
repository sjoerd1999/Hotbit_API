#!../env/bin/python

# https://stackoverflow.com/questions/48562893/how-to-gracefully-terminate-an-asyncio-script-with-ctrl-c
# https://anyio.readthedocs.io/en/stable/signals.html
# https://gitter.im/python-trio/general#
# https://stackoverflow.com/questions/54525836/where-do-i-catch-the-keyboardinterrupt-exception-in-this-async-setup


COPY_AUTH_BLOB_FROM_CHROME = \
{"id":300,"params":[2341316, 1633183637,"web","B8..24"],"method":"server.auth2"}

import json
import aiohttp
import asyncio
import gzip

from signal import SIGINT, SIGTERM

import threading

from time import sleep

import traceback

class WebSocket:
    KEEPALIVE_INTERVAL_S = 10

    def __init__(self, url, on_msg, use_async=False):
        self.url = url
        self.on_msg = on_msg

        # only used when use_async=False
        self.thread_did_setup = False
        self.did_terminate = False
        self.root_task = None

        if use_async:
            self.Q = asyncio.Queue()  # use current loop, get_event_loop() TODO: check this?

        else:
            def worker():

                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)

                self.Q = asyncio.Queue(loop=self.loop)  # RuntimeError: There is no current event loop in thread 'websocket_worker'.

                self.root_task = self.loop.create_task(self.aio_run())

                self.thread_did_setup = True

                try:
                    self.loop.run_until_complete(self.root_task)
                    print('This does not hit')

                except Exception as e:
                    print()
                    print('⛔️ WebSocket::worker Exception:', e)
                    print(traceback.print_exc())
 
                    self.root_task.cancel()
                    self.loop.stop()

                except:
                    print('⛔️ This does not hit')

                finally:
                    print()
                    print('WebSocket::worker finally')

                print('/worker')

            self.worker_thread = threading.Thread(
                name = 'websocket_worker',
                target = worker,
                daemon = True,
                # args = (foo,)
                )

            self.worker_thread.start()

            # Due to some bug, we have to set signal handler from main thread
            while not self.thread_did_setup:
                sleep(0.01)

            for signal in [SIGINT, SIGTERM]:
                self.loop.add_signal_handler(signal, self.root_task.cancel)

    def queue_send(self, J):
        self.Q.put_nowait(J)

    async def aio_run(self):
        print('WebSocket::aio_run')

        async with aiohttp.ClientSession() as session:
            self.ws = await session.ws_connect(self.url)

            print('WebSocket::aio_run Socket Connected')

            async def task_ping():
                while True:
                    print('KEEPALIVE')
                    await self.ws.ping()
                    await asyncio.sleep(WebSocket.KEEPALIVE_INTERVAL_S)

            async def task_message_send():
                while True:
                    J = await self.Q.get()
                    print()
                    print('WebSocket::aio_run task_message_send')
                    print(J)
                    await self.ws.send_json(J)
                    self.Q.task_done()

            async def task_message_recv():
                async for msg in self.ws:
                    def extract_data(msg):
                        if msg.type == aiohttp.WSMsgType.BINARY:
                            as_bytes = gzip.decompress(msg.data)
                            as_string = as_bytes.decode('utf8')
                            as_json = json.loads(as_string)
                            return as_json

                        elif msg.type == aiohttp.WSMsgType.TEXT:
                            return json.loads(msg.data)

                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            print()
                            print('⛔️ aiohttp.WSMsgType.ERROR')

                        return msg.data

                    data = extract_data(msg)

                    try:
                        self.on_msg(data)

                    except Exception as e:
                        print()
                        print('⛔️', e)
                        print(traceback.print_exc())


            self.ping_task         = asyncio.create_task( task_ping() )
            self.message_send_task = asyncio.create_task( task_message_send() )
            self.message_recv_task = asyncio.create_task( task_message_recv() )

            try:
                await asyncio.gather(
                    self.ping_task,
                    self.message_send_task,
                    self.message_recv_task,
                    return_exceptions=True
                )
            except asyncio.CancelledError:
                print()
                print('🔌  WebSocket::aio_run asyncio.CancelledError')

            except:
                print('⚠️ WebSocket::aio_run except -- Should not hit')

            await self.teardown()

            self.did_terminate = True

            print('/WebSocket::aio_run')


    async def teardown(self):
        print('WebSocket::teardown')

        self.ping_task.cancel()
        self.message_send_task.cancel()
        self.message_recv_task.cancel()

        await self.ws.close()

        if self.root_task:
            self.root_task.cancel()

        print('/WebSocket::teardown')

# https://github.com/sjoerd1999/Hotbit_API
# https://github.com/hotbitex/hotbit.io-api-docs/blob/master/websocket_api_en.md

from decimal import Decimal

class WS_HotBit:
    URL = 'wss://ws.hotbit.io'
    STREAM_ID_OFFSET = 42

    AUTH_BLOB = COPY_AUTH_BLOB_FROM_CHROME

    def __init__(self, on_order_update, on_balance_update, on_trades):
        self.on_order_update = on_order_update
        self.on_balance_update = on_balance_update
        self.on_trades = on_trades

        self.did_auth = False

        self.streams = { }

        def on_msg(data):
            print()

            keys = set(data.keys())

            # ⚡️ {'error': None, 'result': {'status': 'success'}, 'id': 2}
            if keys == set(['error', 'result', 'id']):
                print('⚡️', data)
                success = data['result']
                if success:
                    assert data['result']['status'] == 'success'
                glyph = '✅' if success else '❌'

                if success and data['id'] == WS_HotBit.AUTH_BLOB['id']:
                    self.did_auth = True

                id_ = data['id']

                stream = self.streams[id_][0]

                print(stream, glyph)

                if stream == 'server.auth2':
                    if success:
                        print('🔑 Authenticated with HotBit server')
                        self.did_auth = True
                    else:
                        print('☢️  Failed to authenticate with HotBit server')
                else:
                    got_all = set(u[1] for u in self.streams.values()) == {'✅'}
                    if got_all:
                        print('🚀 Subscribed to all streams')

                self.streams[id_][1] = glyph


            elif 'method' in keys:
                stream = data['method']

                if stream == 'deals.update':
                    # ⚡️ {'method': 'deals.update', 'params': ['ETHUSDT', [{'id': 2314238190, 'time': 1623179096.525095, 'price': '2473.46', 'amount': '0.17562', 'type': 'buy'}]], 'id': None, 'ts': 1623179097}
                    id_ = data['id']
                    timestamp = Decimal(data['ts'])
                    payload = data['params']

                    if len(payload) != 2:
                        print('⚡️ deals.update ⚠️ Unknown WebSocket packet format')
                        print(payload)

                    else:
                        symbol, trades = payload
                        print(f'id: {id_}', stream, timestamp, symbol, f'got {len(trades)} trades')

                        on_trades(symbol, trades)

                # ⚡️ {'method': 'asset.update', 'params': [{'BTC': {'freeze': '0', 'available': '0.000011'}}], 'id': None, 'ieo_use': '0'}
                elif stream == 'asset.update':
                    id_ = data['id']
                    payload = data['params']
                    ieo_use = data['ieo_use']

                    # [{'BTC': {'freeze': '0', 'available': '0.000011'}}]
                    if len(payload) > 1:
                        print('⚠️ > 1 item in paylad')

                    payload = payload[0]  # API fail from HotBit, not as documented!

                    balances = { k : (Decimal(v['available']), Decimal(v['freeze'])) for (k, v) in payload.items() }

                    print('⚡️ asset.update:', data)
                    print('💰', balances)

                    self.on_balance_update(balances)

                # ⚡️ {'method': 'order.update', 'params': [3, {'maker_fee': '-0.0005', 'user': 2349216, 'id': 38271662681, 'type': 1, 'market': 'BTCUSDT', 'deal_money': '0.03283474', 'price': '38788.72', 'freeze': '0', 'side': 2, 'source': 'web', 'fee_stock': '', 'ctime': 1623181218.905335, 'deal_fee': '0.000019700844', 'mtime': 1623181218.905351, 'deal_stock': '0.000001', 'amount': '0.000001', 'taker_fee': '0.0006', 'left': '0', 'alt_fee': '0', 'deal_fee_alt': '0', 'status': 1}], 'id': None, 'ts': 1623181218}
                elif stream == 'order.update':
                    id_ = data['id']
                    timestamp = Decimal(data['ts'])


                    status_index, P = data['params']

                    status = ['NEW', 'UPDATE', 'COMPLETED'] [status_index - 1]  # status_index: 1: new order, 2: order update, 3: completed

                    market_limit = ['LIMIT', 'MARKET'] [P['type'] - 1]  # 1-limit order 2 -market order
                    side = ['SELL', 'BUY'] [P['side'] - 1]  # 1-Ask 2-Bid 

                    glyph = {
                        'MARKET-BUY': '🟢',
                        'MARKET-SELL': '🔴',
                        'LIMIT-BUY': '🟩',
                        'LIMIT-SELL': '🟥'
                    }[market_limit + '-' + side]

                    print('⚡️ order.update:', (glyph + ' ') * status_index)
                    print(P)

                    D = {
                        'user_id'           : P['user'],
                        'id'                : P['id'],
                        'status'            : status,
                        'symbol'            : P['market'],
                        'glyph'             : glyph,
                        '_status'           : P['status'],
                        'deal_money'        : Decimal( P['deal_money'] ),
                        'price'             : Decimal( P['price'] ),
                        'frozen'            : Decimal( P['freeze'] ),
                        'deal_stock'        : Decimal( P['deal_stock'] ),
                        'amount'            : Decimal( P['amount'] ),
                        'left'              : Decimal( P['left'] ),
                        'timestamp_creation': float( P['ctime'] ),
                        'timestamp_update'  : float( P['mtime'] ),
                    }

                    print(D)

                    self.on_order_update(P, D)

                else:
                    print('⚠️ Unknown stream from WebSocket')
                    print(data)

            else:
                print('⚠️ Unknown packet from WebSocket')
                print(data)


        self.websocket = WebSocket(WS_HotBit.URL, on_msg)

        if WS_HotBit.AUTH_BLOB:
            self.subscribe('server.auth2', WS_HotBit.AUTH_BLOB['params'], id_=WS_HotBit.AUTH_BLOB['id'])

            while not self.did_auth:
                sleep(0.1)

            self.subscribe('asset.subscribe', ['BTC','USDT'])
            self.subscribe('deals.subscribe', ['ETHUSDT','BTCUSDT'])
            self.subscribe('order.subscribe', ['order','BTCUSDT'])


    def subscribe(self, stream, params, id_=None):
        if not id_:
            id_ = len(self.streams) + WS_HotBit.STREAM_ID_OFFSET

        self.streams[id_] = [stream, 'PENDING']

        self.websocket.queue_send({
            'method': stream,
            'params': params,
            'id': id_
        })


if __name__ == '__main__':
    def on_order_update(raw_blob, E):
        pass

    def on_balance_update(balances):
        pass

    def on_trades(symbol, trades):
        print(f'aiorun(): Got {len(trades)} Trade(s) for {symbol}')
        if len(trades) < 100:
            print([tr['amount'] for tr in trades])

    streamer = WS_HotBit(on_order_update, on_balance_update, on_trades)

    try:
        while not streamer.websocket.did_terminate:
            print('meow')
            sleep(10)

    except KeyboardInterrupt:
        print('Only hits if we disable signal code')

    except:
        print('Does not hit')

    print('ALL DONE')