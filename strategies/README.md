### MEXC SDK 1.0.0 Python docunentation:

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

### To get the above dictionary, run a python code with the following:

from mexc_sdk import Spot
client = Spot(api_key="your_api_key", api_secret="your_api_secret")
print(dir(client))

``` You must have mexc_sdk downloaded from GitHub and installed using pip for
the above import and code usage to work ```
