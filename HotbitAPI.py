import requests

class HotbitAPI(object):
    def __init__(self):
        # Requests session is about 15ms faster than normal requests
        self.session = requests.Session()
        self.base_url = 'https://www.hotbit.io/v1'
        self.headers = {
            'authority': 'www.hotbit.io',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '^\\^',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.hotbit.io',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.hotbit.io/',
            'accept-language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7,lb;q=0.6,de;q=0.5',
            'cookie': ''
        }

    def set_cookie(self, cookie):
        self.headers['cookie'] = cookie
        self.session.headers.update(self.headers)

    # POST a buy or sell order
    def post_order(self, price, quantity, market, side, type):
        data = {
          'price': price,
          'quantity': quantity,
          'market': market,
          'side': side,
          'type': type,
          'hide': 'false',
          'use_discount': 'false'
        }
        return self.session.post(self.base_url + '/order/create?platform=web', data=data).json()

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
        return self.session.post(self.base_url + '/game/balances?platform=web').json()

    # Get info about the user
    def get_user_info(self):
        return self.session.get(self.base_url + '/info?platform=web').json()

    def order_history(self, market, start_time, end_time, page, page_size):
        params = {
            'start_time': start_time,
            'end_time': end_time,
            'market': market.replace('/', ''),
            'page': page,
            'page_size': page_size,
            'platform': 'web'
        }
        return self.session.get(self.base_url + '/order/history', params=params).json()

    def trade_history(self, market, start_time, end_time, page, page_size):
        data = {
            'startTime': start_time,
            'endTime': end_time,
            'market': market.replace('/', ''),
            'side': 0,
            'hideCanceled': True,
            'pageNum': page,
            'numPerPage': page_size,
            'platform': 'web'
        }
        return self.session.post(self.base_url + '/trade/history/query', data=data).json()

