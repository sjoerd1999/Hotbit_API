import threading
import json
import aiohttp
import asyncio
import gzip
import time

class HotbitWS:
    def __init__(self, callback, key=None):
        self.ws = None
        self.key = key
        self.callback = callback
        self.methods = ['server.auth2']

        # Run in a thread so it doesn't block
        loop = asyncio.get_event_loop()
        threading.Thread(target=loop.run_until_complete, args=[self.run()], daemon=True).start()
        # Send ping every 10 seconds to keep connection alive
        asyncio.run_coroutine_threadsafe(self.keep_alive(10), loop)

    def subscribe(self, method, params=[]):
        if method not in self.methods:
            self.methods.append(method)
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self._subscribe(method, params, self.methods.index(method)), loop)

    async def _subscribe(self, method, params, id_):
        await self.ws.send_json({"method": method, "params": params, "id": id_})

    async def keep_alive(self, sleep):
        while True:
            await asyncio.sleep(sleep)
            await self.ws.ping()

    async def run(self):
        session = aiohttp.ClientSession()
        self.ws = await session.ws_connect('wss://ws.hotbit.io')

        if key is not None:
            await self.ws.send_json({"id": 0, "params": self.key, "method": "server.auth2"})  # auth

        def extract_data(msg):
            if msg.type == aiohttp.WSMsgType.BINARY:
                as_bytes = gzip.decompress(msg.data)
                as_string = as_bytes.decode('utf8')
                as_json = json.loads(as_string)
                return as_json
            else:
                print('FAILED to decompress')
                return msg.data

        while True:
            data = await self.ws.receive()
            data_ = extract_data(data)
            if 'method' in data_.keys():
                method = data_['method']
            else:
                method = self.methods[data_['id']]
            self.callback(method, data_)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def callback_(method, msg):
    if method == 'server.auth2':
        if msg['result'] is not None:
            print('Logged in successfully!')
        else:
            print('Logging in failed :(')

    if method == 'balance.query':
        print('New balance: ', msg['result'])

    if method == 'deals.update':
        print('New deal: ', msg)

key = [23....., 1622920122, "web", "7EC20................082930CB"]  # insert key here
ws = HotbitWS(callback_, key)

time.sleep(3)  # Wait for the websocket to start up and log in

ws.subscribe('deals.subscribe', params=['BTCUSDT', 'ETHUSDT', 'ADAUSDT'])  # subscribe to a public stream

while True:
    time.sleep(5)
    ws.subscribe('balance.query')  # ask for a private query

