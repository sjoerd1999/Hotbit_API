import requests
import time

class HotbitAPI(object):
    def __init__(self, cookie):
        # Requests session is about 15ms faster than normal requests
        self.session = requests.Session()
        self.base_url = 'https://www.hotbit.io/v1'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'referer': 'https://www.hotbit.io/',
            'cookie': cookie
        }
        self.session.headers.update(self.headers)
        print('Fetching precisions...')
        prec = self.session.get('https://api.hotbit.io/api/v1/market.list').json()['result']
        self.precisions = {p['name']: [p['money_prec'], p['min_amount']] for p in prec}
        self.prices = {}
        print('Fetching prices...')
        self.updatePrices()

    # POST a buy or sell order
    def post_order(self, price, quantity, market, side, type):
        prec = self.precisions[market.replace('/', '')]
        price_ = str(round(price, prec[0]))
        quantity_ = str(round(quantity, (prec[1].index('1') - 1) if '.' in prec[1] else (1 - len(prec[1]))))
        data = {
          'price': price_,
          'quantity': quantity_,
          'market': market,
          'side': side,
          'type': type,
          'hide': 'false',
          'use_discount': 'false'
        }
        return self.session.post(self.base_url + '/order/create', data=data).text

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

    def updatePrices(self):
        tickers = self.session.get('https://api.hotbit.io/api/v1/allticker').json()['ticker']
        self.prices = {t['symbol'].replace('_', '/'): t['last'] for t in tickers}

    def updatePricesThread(self):
        while True:
            self.updatePrices()
            time.sleep(0.5)

    def buy(self, symbol, tot_usdt, mult):
        price = float(self.prices[symbol]) * mult
        quantity = tot_usdt / price
        print('BUY:', symbol, price, quantity)
        buy_ = self.post_order(price=price, quantity=quantity, market=symbol, side='BUY', type='LIMIT')
        print(buy_)
        return price, quantity

    def sell(self, symbol, price, quantity):
        print('SELL:', symbol, price, quantity)
        sell_ = self.post_order(price=price, quantity=quantity, market=symbol, side='SELL', type='LIMIT')
        print(sell_)
