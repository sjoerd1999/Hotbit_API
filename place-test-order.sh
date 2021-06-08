#!/bin/bash

# curl 'https://www.hotbit.io/v1/order/create?platform=web' \
#   -H 'authority: www.hotbit.io' \
#   -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"' \
#   -H 'accept: application/json, text/plain, */*' \
#   -H 'sec-ch-ua-mobile: ?0' \
#   -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36' \
#   -H 'content-type: application/x-www-form-urlencoded' \
#   -H 'origin: https://www.hotbit.io' \
#   -H 'sec-fetch-site: same-origin' \
#   -H 'sec-fetch-mode: cors' \
#   -H 'sec-fetch-dest: empty' \
#   -H 'referer: https://www.hotbit.io/' \
#   -H 'accept-language: en-US,en;q=0.9' \
#   -H 'cookie: __cfruid=fd..07; _uab_collina=16..38; lang=en-US; hotbit=05..1e; _ga=..; _gid=..; islogin=true' \
#   --data-raw 'price=38788.72&quantity=0.000258&market=BTC%2FUSDT&side=BUY&type=LIMIT&hide=false&use_discount=false' \
#   --compressed

# max 6 DP allowed for quantity, 0.000001 (BTC) works (~$.04)

  # -v \
  # --trace-time \

#curl 'https://www.hotbit.io/v1/order/create' \
#  -v \
#  --trace-time \
#  -H 'referer: https://www.hotbit.io/' \
#  -H 'cookie: hotbit=05..1e' \
#  --data-raw 'price=38788.72&quantity=0.000001&market=BTC/USDT&side=BUY&type=LIMIT&hide=true&use_discount=false'

echo

curl 'https://www.hotbit.io/v1/order/create' \
  -H 'referer: https://www.hotbit.io/' \
  -H 'cookie: hotbit=05..1e' \
  --data-raw 'price=38788.72&quantity=0.000001&market=BTC/USDT&side=BUY&type=LIMIT&hide=true&use_discount=false'
