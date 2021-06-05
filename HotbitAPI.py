#!../env/bin/python

# import httpx

# BASE_URL = 'https://www.hotbit.io/v1/'

# class HotBitAPI:
#     def __init__(self, cookie):
#         self.cookie = cookie


#         r = self.get('market.list')

#         print(r)


#     def post(self, stub, data):
#         headers = {
#             'referer': 'https://www.hotbit.io/',
#             'cookie': f'hotbit={self.cookie}',
#         }

#         r = httpx.post(BASE_URL + stub, headers=headers, data=data)

#         print('Returned code: ', r.status_code)

#         print(r.json())
#         return r.json()

#     def get(self, stub):
#         headers = {
#             'referer': 'https://www.hotbit.io/',
#             'cookie': f'hotbit={self.cookie}',
#         }

#         r = httpx.get(BASE_URL + stub, headers=headers)

#         print('Returned code: ', r.status_code)

#         print(r.text)
#         return r.text

# HOTBIT_COOKIE = '05a...81e'

# HotBitAPI(HOTBIT_COOKIE)

# exit(0)

import json

from decimal import Decimal

import requests

# 🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥

class HotbitAPI(object):
    def __init__(self, key):
        # Requests session is about 15ms faster than normal requests
        self.session = requests.Session()
        self.base_url = 'https://www.hotbit.io/v1'

        self.session.headers.update({
            'referer': 'https://www.hotbit.io/',
            'cookie': f'hotbit={key}'
        })

        # J = self.get(base_url= 'market.list')['result']  # can't, as this uses API URL not web URL

        J = self.session.get('https://api.hotbit.io/api/v1/market.list').json()['result']

        # [{'money_prec': 10, 'stock_prec': 2, 'name': 'QASHBTC', 'fee_prec': 4, 'stock': 'QASH', 'money': 'BTC', 'min_amount': '0.1'}, ...

        self.symbol_meta= {
            m['name']: m
                for m in J
        }

        self.precisions = {
            k: (v['money_prec'], v['min_amount'])
                for k,v in self.symbol_meta.items()
        }


    def get(self, stub, **kwargs):
        r = self.session.get(self.base_url + '/' + stub, **kwargs).json()

        print('⚡️', r)
        return r


    def post(self, stub, **kwargs):
        print('POST-ing to endpoint:', stub)
        print(kwargs)

        r = self.session.post(self.base_url + '/' + stub, **kwargs).json()

        print('⚡️', r)
        return r


    # POST a buy or sell order
    def post_order(self, price, quantity, market, side, type, dry_run=False):
        if '/' not in market:
            market = market[:-4] + '/USDT'

        # Format the price and quantity properly so we don't get errors
        meta = self.symbol_meta[market.replace('/', '')]

        prec = meta['money_prec']
        price = round(float(price), prec)

        # handles '0.01' and '100'
        min_amt =  Decimal(meta['min_amount'])
        quantity_quantized = str(Decimal(quantity).quantize(min_amt))

        print('min_amt', min_amt)
        print('quantized by min_amt', min_amt, ', quantity', quantity, '->', quantity_quantized)

        # s = meta['min_amount']  # string
        # quantity = str(round(quantity, s.index('1') - (s.index('.') if '.' in s else len(s))))

        data = {
          'price': price,
          'quantity': quantity_quantized,
          'market': market,
          'side': side,
          'type': type,
          'hide': False,
          'use_discount': False
        }

        glyph = {'BUY':'🟩', 'SELL':'🟥'}[side]

        print(glyph, 'Placing order:')
        print(data)

        if dry_run:
            return None, None

        r = self.post('order/create', data=data)

        order_id = r['Content']['id'] if r['Msg'] == 'success' else None

        return order_id, r

    # Cancel an order (needs both market and order-id)
    def cancel_order(self, market, order_id):
        data = {
            'market': market.replace('/', ''),
            'order_id': order_id
        }

        print('❌ Cancelling order:')
        print(data)

        return self.post('order/cancel', data=data)


    # Cancel one or multiple orders (pass an id or a list of ids)
    def cancel_orders(self, market, order_ids):
        data = [
            {
                'market': market.replace('/', ''),
                'order_id': id_
            }
            for id_ in order_ids
        ]

        print('❌ ❌ Cancelling orders:')
        print(data)

        return self.post('order/cancel_all', data=json.dumps(data))


    # Get all user balances
    def get_balances(self):
        # {'Code': 1100, 'Msg': 'success', 'Content': {'EOS': {'available': '0', 'freeze': '0'}, ...}}
        r = self.post('/game/balances')

        if r['Msg'] != 'success':
            print('⛔️ Failed to fetch balances')
            return None

        print('⚡️', r)

        str2float = lambda D: { k : float(v)  for k, v in D.items() }

        # e.g. balances['EOS']['available'] = 4.2
        balances = { k : str2float(v)  for k, v in r['Content'].items() }

        return balances


    # Get info about the user
    def get_user_info(self):
        print('🔸 Fetching userinfo')

        r = self.get('/info')

        print('⚡️', r)

        return r


    # Get order history (does not include unfilled active orders)
    # Scraped from https://www.hotbit.io/trade/orderhistory
    def order_history(self, market, start_time, end_time=None, page=1, page_size=20):
        params = {
            'start_time': int(start_time),
            'end_time': int(end_time or time()+60),
            'market': market.replace('/', ''),
            'page': page,
            'page_size': page_size,
            # 'platform': 'web'
        }

        print('🔸 Fetching order history:')
        print(params)

        r = self.get('order/history', params=params)

        # {
        #     'Code': 1100,
        #     'Msg': 'success',
        #     'Content': {
        #         'data': [
        #             {'id': 37693965599, 'create_time': 1622880382.896458, 'finish_time': 1622880382.896462, 'user_id': 2349216, 'market': 'BTCUSDT', 'source': 'web', 't': 1, 'side': 1, 'price': '37488.24', 'amount': '0.000001', 'taker_fee': '0.0006', 'maker_fee': '-0.0005', 'deal_stock': '0.000001', 'deal_money': '0.03752855', 'deal_fee': '0.00002251713', 'status': 0, 'deal_fee_alt': '0', 'alt_fee': '-0.0005', 'fee_stock': ''},
        #             :
        #         ],
        #         'page_nextid': 0
        #     }
        # }

        if r['Msg'] != 'success':
            print('⛔️ Failed to fetch order history')
            return None

        orders = r['Content']['data']

        orders_dict = { o['id']: o for o in orders }
        return orders_dict


    # Scraped from https://www.hotbit.io/trade/order
    def trade_history(self, market, start_time, end_time=None, page=1, page_size=20):
        data = {
            'startTime': int(start_time),
            'endTime': int(end_time or time()),
            'market': market.replace('/', ''),
            'side': 0,
            'hideCanceled': True,
            'pageNum': page,
            'numPerPage': page_size,
        }

        print('🔸 Fetching trade history:')
        print(data)

        return self.post('/trade/history/query', data=data)


    # Get account deposit history
    def deposit_history(self, page=1, page_size=20):
        data = {
            'categories': 1,
            'pageNum': page,
            'numPerPage': page_size
        }

        print('🔸 Fetching deposit history:')
        print(data)

        return self.post('/fund/history/query?platform=web', data=data)


    # Get account withdrawal history
    def withdraw_history(self, page=1, page_size=20):
        data = {
            'categories': 2,
            'pageNum': page,
            'numPerPage': page_size
        }

        print('🔸 Fetching withdraw history:')
        print(data)

        return self.post('/fund/history/query?platform=web', data=data)


# 🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥

CURRENT_BTC_PRICE = 35000

from time import time, sleep

import json

# Need to create hotbit.json like this:
#     {
#         "hotbit_cookie": "05a...81e"
#     }


if __name__ == '__main__':

    with open('hotbit.json') as f:
        data = json.load(f)
        hotbit_cookie = data['hotbit_cookie']

    print()
    print('Current timestamp:', time())

    print()
    print('🔸 🔸 🔸  Creating Connection to HotBit')

    hotbit = HotbitAPI(hotbit_cookie)

    usdt_symbols = set(
        k for k, v in hotbit.symbol_meta.items()
            if k[-4:] == 'USDT'
    )

    print()
    print('🔹 HotBit supports', len(usdt_symbols), 'USDT Symbols:')
    print(sorted(usdt_symbols)[:10], ', ...')

    print()
    print('🔹 Meta for ADAUSDT:')
    print(hotbit.symbol_meta['ADAUSDT'])

    mins = set( v['min_amount'] for v in hotbit.symbol_meta.values() )
    precs = set( v['money_prec'] for v in hotbit.symbol_meta.values() )

    print()
    print('🔹 MinAmounts:', sorted(mins))
    print('🔹 Precisions:', sorted(precs))

    print()
    print('🔸 🔸 Fetching balances')

    balances = hotbit.get_balances()
    print('USDT balance:', balances['USDT']['available'])

    if balances['USDT']['available'] == 0:
        print('⛔️ balance is reporting as 0')


    print()
    print('🔸 🔸 withdraw / deposit history')

    r = hotbit.deposit_history()
    r = hotbit.withdraw_history()

    print()
    print()
    print('🔸 🔸 Testing orders')

    min_qty = Decimal(hotbit.symbol_meta['BTCUSDT']['min_amount'])

    print()
    print('🟩  min_qty limit BUY on BTC/USDT with LOW price, so it will NOT be filled')
    order_id__nonfill, r = hotbit.post_order(market='BTC/USDT', price=CURRENT_BTC_PRICE/2, quantity=min_qty, side='BUY', type='LIMIT')

    print('...✅' if r['Msg'] == 'success' else '⛔️')

    print()
    print('🟩  1/2 min_qty limit BUY on BTC/USDT (expect fail)')
    no_order_id_as_fail, r = hotbit.post_order(market='BTC/USDT', price=CURRENT_BTC_PRICE/2, quantity=min_qty/2, side='BUY', type='LIMIT')

    print('...✅' if r['Msg'] == 'error quantity' else '⛔️')


    print()
    print('🟩  Making a BUY order that WILL complete')
    order_id__will_fill, r = hotbit.post_order(market='BTC/USDT', price=CURRENT_BTC_PRICE*2, quantity=min_qty, side='BUY', type='LIMIT')

    print('...✅' if r['Msg'] == 'success' else '⛔️')


    print()
    print('🟥  Making a SELL order that WILL complete')
    order_id__will_fill, r = hotbit.post_order(market='BTC/USDT', price=CURRENT_BTC_PRICE*2, quantity=min_qty, side='BUY', type='LIMIT')

    print('...✅' if r['Msg'] == 'success' else '⛔️')


    print()
    print('Waiting 5s...')
    sleep(5)


    print()
    print('❌ testing cancel_order')

    print('Cancelling order that did not fill:', order_id__nonfill)

    r = hotbit.cancel_order('BTC/USDT', order_id__nonfill)

    print('...✅' if r['Msg'] == 'sucessfully cancelled' else '⛔️ Problem with cancel')

    print()
    
    print('❌ ❌ testing cancel_all')

    print('Placing 2 orders which will not fill, to test cancel-all')

    sides = ['BUY', 'SELL', 'BUY']
    ids = []
    for side in ['BUY', 'SELL']:
        price = CURRENT_BTC_PRICE/2 if side == 'BUY' else CURRENT_BTC_PRICE*2
        id_, r = hotbit.post_order(market='BTC/USDT', price=price, quantity=min_qty, side=side, type='LIMIT')
        ids.append(id_)

    print()
    print('Waiting 5s...')
    sleep(5)

    print('Cancelling ids:', ids)

    r = hotbit.cancel_orders('BTC/USDT', ids)


    print('...✅ ' if r['Msg'] == 'all orders are sucessfully cancelled' else '⛔️')

    print()
    print('🔸 🔸 Order History, last minute')

    r = hotbit.order_history('BTC/USDT', start_time=time()-60)

    print()
    print('OrderIds:', r.keys())

    print()
    print('...✅ Found' if order_id__will_fill in r.keys() else '⛔️ Failed to find', 'first completed order in order_history')


    print()
    print('🔸 🔸 Trade History, last 30 minute')

    r = hotbit.trade_history(market='', start_time=time()-60)
