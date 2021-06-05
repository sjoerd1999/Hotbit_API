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
        return self.session.get(self.base_url + '/' + stub, **kwargs).json()


    def post(self, stub, **kwargs):
        return self.session.post(self.base_url + '/' + stub, **kwargs).json()


    # POST a buy or sell order
    def post_order(self, price, quantity, market, side, type):
        price, quantity = float(price), float(quantity)

        # Format the price and quantity properly so we don't get errors
        meta = self.symbol_meta[market.replace('/', '')]

        price = round(float(price), meta['money_prec'])

        min_amt = meta['min_amount']
        if '.' in min_amt:
            dps = len(min_amt.split('.')[1])
            quantity = round(quantity, dps)

        data = {
          'price': price,
          'quantity': quantity,
          'market': market,
          'side': side,
          'type': type,
          'hide': False,
          'use_discount': False
        }

        response = self.post('order/create', data=data)

        order_id = response['Content']['id'] if response['Msg'] == 'success' else None

        return order_id, response

    # Cancel an order (needs both market and order-id)
    def cancel_order(self, market, order_id):
        data = {
            'market': market.replace('/', ''),
            'order_id': order_id
        }
        return self.session.post(self.base_url + '/order/cancel?platform=web', data=data).json()


    # Cancel multiple orders (needs market and order-ids for each one)
    def cancel_all(self, market, order_ids):
        data = [{'market': market.replace('/', ''), 'order_id': o} for o in order_ids]
        return self.session.post(self.base_url + '/order/cancel?platform=web', data=data).json()


    # Get all user balances
    def get_balances(self):
        # {'Code': 1100, 'Msg': 'success', 'Content': {'EOS': {'available': '0', 'freeze': '0'}, ...}}
        r = self.post('/game/balances')

        if r['Msg'] != 'success':
            print('⛔️ Failed to fetch balances')
            return None

        print(r)

        str2float = lambda D: { k : float(v)  for k, v in D.items() }

        # e.g. balances['EOS']['available'] = 4.2
        balances = { k : str2float(v)  for k, v in r['Content'].items() }

        return balances


    # Get info about the user
    def get_user_info(self):
        return self.session.get(self.base_url + '/info?platform=web').json()


    # Get order history (does not include unfilled active orders)
    def order_history(self, market, start_time, end_time=None, page=1, page_size=20):
        params = {
            'start_time': int(start_time),
            'end_time': int(end_time or time()+60),
            'market': market.replace('/', ''),
            'page': page,
            'page_size': page_size,
            # 'platform': 'web'
        }

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


    # Get trade history
    def trade_history(self, market, start_time, end_time=None, page=1, page_size=20):
        data = {
            'start_time': int(start_time),
            'end_time': int(end_time or time()),
            'market': market.replace('/', ''),
            'side': 0,  # TODO: 0 or 1?
            'hideCanceled': True,
            'pageNum': page,
            'numPerPage': page_size,
            # 'platform': 'web'
        }
        return self.session.post(self.base_url + '/trade/history/query', data=data).json()


    # Get account deposit history
    def deposit_history(self, page=1, page_size=20):
        data = {
            'categories': 1,
            'pageNum': page,
            'numPerPage': page_size
        }
        return self.session.post(self.base_url + '/fund/history/query?platform=web', data=data).json()


    # Get account withdrawal history
    def withdraw_history(self, page=1, page_size=20):
        data = {
            'categories': 2,
            'pageNum': page,
            'numPerPage': page_size
        }
        return self.session.post(self.base_url + '/fund/history/query?platform=web', data=data).json()


# 🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥  🐥


TEST_ORDERS = True

CURRENT_BTC_PRICE = 35000

from time import time, sleep

import json

# Need to create hotbit.json like this:
#     {
#         "hotbit_cookie": "05a...81e"
#     }
with open('hotbit.json') as f:
    data = json.load(f)
    hotbit_cookie = data['hotbit_cookie']

if __name__ == '__main__':
    hotbit = HotbitAPI(hotbit_cookie)

    usdt_symbols = set(
        k for k, v in hotbit.symbol_meta.items()
            if k[-4:] == 'USDT'
    )

    print('HotBit supports', len(usdt_symbols), 'USDT Symbols:')
    print(sorted(usdt_symbols)[:10], ', ...')

    print()
    print('Meta for ADAUSDT:')
    print(hotbit.symbol_meta['ADAUSDT'])

    mins = set( v['min_amount'] for v in hotbit.symbol_meta.values() )
    precs = set( v['money_prec'] for v in hotbit.symbol_meta.values() )

    print()
    print('MinAmounts:', sorted(mins))
    print('Precisions:', sorted(precs))

    balances = hotbit.get_balances()
    print()
    print('USDT balance:', balances['USDT']['available'])

    if balances['USDT']['available'] == 0:
        print('⛔️ balance is reporting as 0')

    print()
    print('Current timestamp:', time())

    if TEST_ORDERS:
        print()
        print('min_qty limit BUY on BTC/USDT with LOW price, so it will NOT be filled')
        order_id__nonfill, response = hotbit.post_order(market='BTC/USDT', price=CURRENT_BTC_PRICE/2, quantity=hotbit.symbol_meta['BTCUSDT']['min_amount'], side='BUY', type='LIMIT')

        print(response)
        assert(response['Msg'] == 'success')

        print()
        print('1/2 min_qty limit BUY on BTC/USDT (expect fail)')
        no_order_id_as_fail, response = hotbit.post_order(market='BTC/USDT', price=CURRENT_BTC_PRICE/2, quantity=float(hotbit.symbol_meta['BTCUSDT']['min_amount'])/2, side='BUY', type='LIMIT')

        print(response)
        assert(response['Msg'] == 'error quantity')

        print()
        print('Making an order that WILL complete')
        order_id__will_fill, response = hotbit.post_order(market='BTC/USDT', price=CURRENT_BTC_PRICE*2, quantity=hotbit.symbol_meta['BTCUSDT']['min_amount'], side='BUY', type='LIMIT')

        print(response)
        assert(response['Msg'] == 'success')

    print()
    print('Waiting 10s before fetching order history')
    sleep(10)

    print()
    print('Order History, last hour')
    r = hotbit.order_history('BTC/USDT', start_time=time()-3600)
    print(r)

    print()
    print('OrderIds:', r.keys())

    print()
    print('Found' if order_id__will_fill in r.keys() else '⛔️ Failed to find', 'our completed order in order_history')

