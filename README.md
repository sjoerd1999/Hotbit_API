# Hotbit_API
A funky Python implementation to get around Hotbits 'API is for market makers only blah blah blah' bullshits

## Description
Hotbit only has API-keys available for Market Makers at the moment: https://hotbit.zendesk.com/hc/en-us/articles/360042708374
With some digging, parts of the API-funcionality can be reverse-engineered by looking at requests the website makes while interacting with the browser application

## How to setup

Go to https://www.hotbit.io/

-Go to inspect elements, then navigate to the 'network' tab

-Refresh the page

-Search for the 'info?platform=web' request in the left bar, and select it

-Scroll down a bit and copy the full 'cookie' field (yellow)
![image](https://user-images.githubusercontent.com/35689067/120706985-0e6e4180-c4ba-11eb-956a-5d394677b161.png)

That's all! Now you have everything you need to use the API :)

## Hot to use

Create an API instance:

```
from HotbitAPI import HotbitAPI
hotbit = HotbitAPI()
cookie = ''  # Insert your copied cookie in here
hotbit.set_cookie(cookie)

```

Methods:

```
# Get info about the logged in user
user_info = hotbit.get_user_info()

# Get the free & locked users balances
balances = hotbit.get_balances()

# Post an order
order = hotbit.post_order(price='38000', quantity='0.0001', market='BTC/USDT', side='BUY', type='LIMIT')

# Cancel an order, needs both market and order_id
cancel = hotbit.cancel_order(market='BTC/USDT', order_id=23094920)

# Cancel multiple orders at once
hotbit.cancel_all(market='BTC/USDT', order_ids=[12342232, 45672345])

# Get order history (market can be left empty '' to get all orders for all symbols)
order_history = hotbit.order_history(market='BTC/USDT', start_time=1622066400, end_time=round(time.time()), page=1, page_size=20)

# Get trade history (market can be left empty '' to get all trades for all symbols)
trade_history = hotbit.trade_history(market='BTC/USDT', start_time=1622066400, end_time=round(time.time()), page=1, page_size=20)

```
