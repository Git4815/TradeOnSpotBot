# Strategies

This directory contains the trading strategies and API interaction logic for the TradeOnSpotBot.

## MEXC SDK 1.0.0 Python Documentation

The bot uses the `mexc-sdk` Python library to interact with the MEXC exchange. Below are key methods used:

- **Spot Client Methods**:
  - `klines(symbol, interval, limit)`: Fetches Kline/candlestick data.
  - `account_info()`: Retrieves account balance information.
  - `open_orders(symbol)`: Queries open orders for a symbol.
  - `new_order(symbol, side, order_type, qty, price)`: Places a new order.
  - `cancel_order(symbol, order_id)`: Cancels an order.

For full documentation, refer to the [MEXC API Docs](https://mexcdevelop.github.io/apidocs/spot_v3/en/) or the `mexc-sdk` PyPI page.

## Files

- `API_SDK_Tools.py`: SDK-based API calls.
- `API_Requests.py`: HTTP-based API calls (placeholders).
- `feeder.py`: Manages API interactions, preferring HTTP over SDK.
- `scanner.py`: Selects trading strategies based on Kline spread.
- `high_spread_004/`: High-spread strategy (max 3 orders).
- `low_spread_001/`: Low-spread strategy (max 1 order).

### MEXC SDK 1.0.0 Python code commands

['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', 
'__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', 
'__hash__', '__init__', '__init_subclass__', '__jsii_declared_type__', 
'__jsii_ref__', '__jsii_type__', '__le__', '__lt__', '__module__', '__ne__', 
'__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', 
'__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'account_info', 
'account_trade_list', 'agg_trades', 'all_orders', 'avg_price', 'book_ticker', 
'cancel_open_orders', 'cancel_order', 'config', 'depth', 'exchange_info', 
'historical_trades', 'klines', 'new_order', 'new_order_test', 'open_orders', 
'ping', 'public_request', 'query_order', 'sign_request', 'ticker24hr', 
'ticker_price', 'time', 'trades']

``` To get the above dictionary, run a python code with the following:```

from mexc_sdk import Spot
client = Spot(api_key="your_api_key", api_secret="your_api_secret")
print(dir(client))

# You must have mexc_sdk downloaded from GitHub and installed using pip for
# the above import and code usage to work

### MEXC SDK 1.0.0 Python code new_order commands:

['__call__', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', 
'__format__', '__func__', '__ge__', '__getattribute__', '__getstate__', 
'__gt__', '__hash__', '__init__', '__init_subclass__', '__jsii_name__', 
'__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', 
'__repr__', '__self__', '__setattr__', '__sizeof__', '__str__', 
'__subclasshook__']

``` To get the above dictionary, run a python code with the following:```

from mexc_sdk import Spot
client = Spot(api_key="your_api_key", api_secret="your_api_secret")
print(dir(client.new_order))


# You must have mexc_sdk downloaded from GitHub and installed using pip for
# the above import and code usage to work
