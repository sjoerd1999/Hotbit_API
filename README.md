# Hotbit_API
A funky Python implementation to get around Hotbits 'API is for market makers only blah blah blah' bullshits

## Description
Hotbit only has API-keys available for Market Makers at the moment: https://hotbit.zendesk.com/hc/en-us/articles/360042708374

With some digging, parts of the API-funcionality can be reverse-engineered by looking at requests the website makes while interacting with the browser application

## How to setup

Go to https://www.hotbit.io/, make sure you're logged in

-Go to inspect elements, then navigate to the 'network' tab

-Refresh the page

-Search for the 'info?platform=web' request in the left bar, and select it

-Go to the 'header' tab, scroll down a bit, and copy the FULL COOKIE

This will be your personal 'API' key, keep this private.
![image](https://user-images.githubusercontent.com/35689067/120799363-ec6ad280-c53e-11eb-88a9-1c16503bcfba.png)

That's all! Now you have everything you need to use the API :)

## Hot to use

Create an API instance:

```
from HotbitAPI import HotbitAPI

cookie = '_uab_collina=162179400601847897156348; lang=en-US; _ga=GA1.....................................................' # Insert your cookie here
hotbit = HotbitAPI(cookie)
```

(You may need to update 'User Agent' in the API to match the user agent of your browser)

Methods:

```
# Get info about the logged in user
user_info = hotbit.get_user_info()

# Get the free & locked users balances !! Currently doesn't work, always returns 0, need to figure this out !!
balances = hotbit.get_balances()

# Post an order
order = hotbit.post_order(price=38432, quantity=0.00013, market='BTC/USDT', side='BUY', type='LIMIT')

# Cancel an order, needs both market and order_id
cancel = hotbit.cancel_order(market='BTC/USDT', order_id=23094920)

# Cancel multiple orders at once
cancel_all = hotbit.cancel_all(market='BTC/USDT', order_ids=[12342232, 45672345])

# Get order history (market can be left empty '' to get all orders for all symbols)
order_history = hotbit.order_history(market='BTC/USDT', start_time=1622066400, end_time=round(time.time()), page=1, page_size=20)

# Get trade history (market can be left empty '' to get all trades for all symbols)
trade_history = hotbit.trade_history(market='BTC/USDT', start_time=1622066400, end_time=round(time.time()), page=1, page_size=20)

# Get withdrawal history
withdrawal_history = hotbit.withdraw_history(page=1, page_size=10)

# Get deposit history
deposit_history = hotbit.deposit_history(page=1, page_size=10)
```

## Websocket

For access to the private websocket, again, go a random hotbit page while being logged in, and go to devtools->network.

- Look for ws.hotbit.io
- Go to the 'message' tab
- Click on the message that included 'server.auth2'
- Copy the full array, [231230,163094234,'web','KLSJDF0349903FSLFJL']. This contains your UID, timestamp, platform and signature

![image](https://user-images.githubusercontent.com/35689067/120903048-18bc4700-c644-11eb-96e9-ca8b62a9e6d0.png)

The copied array (key) is only valid for 5 minutes. Existing connections will remain open, but if new connections have to be initialized, a new key must be generated and copied

Example code:

```
from HotbitWS import HotbitWS

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

key = [23-----, 16-----122, "web", "7E-----------------0CB"] # copy your own key here
ws = HotbitWS(callback_, key)

time.sleep(3)  # Wait for the websocket to start up and log in

ws.subscribe('deals.subscribe', params=['BTCUSDT', 'ETHUSDT', 'ADAUSDT'])  # subscribe to a public stream

while True:
    time.sleep(5)
    ws.subscribe('balance.query')  # ask for a private query
```

## Some notes

Market orders are not available on Hotbit, instead, you can put a limit order higher than the current price, which will fill it like a market order.
Do note that setting limit orders above +800% is not allowed

For access to public endpoints/websocket, the normal Hotbit API can be used: https://github.com/hotbitex/hotbit.io-api-docs
