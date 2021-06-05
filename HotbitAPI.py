import requests

class HotbitAPI(object):
    def __init__(self, key):
        # Requests session is about 15ms faster than normal requests
        self.session = requests.Session()
        self.base_url = 'https://www.hotbit.io/v1'
        self.headers = {
            'referer': 'https://www.hotbit.io/',
            'cookie': 'hotbit=' + key
        }
        self.session.headers.update(self.headers)
        prec = self.session.get('https://api.hotbit.io/api/v1/market.list').json()['result']
        self.precisions = {p['name']: [p['money_prec'], p['min_amount']] for p in prec}

    # POST a buy or sell order
    def post_order(self, price, quantity, market, side, type):
        prec = self.precisions[market.replace('/', '')]
        price_ = str(round(price, prec[0]))
        quantity_ = str(round(quantity, (prec[1].index('1') - 1) if '.' in prec[1] else len(prec[1])))
        data = {
          'price': price_,
          'quantity': quantity_,
          'market': market,
          'side': side,
          'type': type,
          'hide': 'false',
          'use_discount': 'false'
        }
        return self.session.post(self.base_url + '/order/create', data=data).json()

    # Cancel an order (needs both market and order-id)
    def cancel_order(self, market, order_id):
        data = {
            'market': market.replace('/', ''),
            'order_id': order_id
        }
        return self.session.post(self.base_url + '/order/cancel', data=data).json()

    # Cancel multiple orders (needs market and order-ids for each one)
    def cancel_all(self, market, order_ids):
        data = [{'market': market.replace('/', ''), 'order_id': o} for o in order_ids]
        return self.session.post(self.base_url + '/order/cancel', data=data).json()

    # Get all user balances
    def get_balances(self):
        return self.session.post(self.base_url + '/game/balances').json()

    # Get info about the user
    def get_user_info(self):
        return self.session.get(self.base_url + '/info').json()

    # Get order history (does not include unfilled active orders)
    def order_history(self, market, start_time, end_time, page=1, page_size=20):
        params = {
            'start_time': start_time,
            'end_time': end_time,
            'market': market.replace('/', ''),
            'page': page,
            'page_size': page_size,
        }
        return self.session.get(self.base_url + '/order/history', params=params).json()

    # Get trade history
    def trade_history(self, market, start_time, end_time, page=1, page_size=20):
        data = {
            'startTime': start_time,
            'endTime': end_time,
            'market': market.replace('/', ''),
            'side': 0,
            'hideCanceled': False,
            'pageNum': page,
            'numPerPage': page_size,
        }
        return self.session.post(self.base_url + '/trade/history/query', data=data).json()

    # Get account deposit history
    def deposit_history(self, page=1, page_size=20):
        data = {
            'categories': 1,
            'pageNum': page,
            'numPerPage': page_size
        }
        return self.session.post(self.base_url + '/fund/history/query', data=data).json()

    # Get account withdrawal history
    def withdraw_history(self, page=1, page_size=20):
        data = {
            'categories': 2,
            'pageNum': page,
            'numPerPage': page_size
        }
        return self.session.post(self.base_url + '/fund/history/query', data=data).json()
