import logging
from mexc_sdk import Spot
from config import Config
from strategies.API_Requests import get_klines_http, get_balance_http, place_order_http, query_open_orders_http, cancel_order_http
from strategies.API_SDK_Tools import get_klines_sdk, get_balance_sdk, place_order_sdk, query_open_orders_sdk, cancel_order_sdk

logger = logging.getLogger(__name__)

class Feeder:
    def __init__(self, config: Config):
        self.config = config
        self.client = Spot(api_key=config.API_KEY, api_secret=config.API_SECRET)

    async def get_klines(self):
        """Fetch Klines, preferring HTTP."""
        result = await get_klines_http(self.config)
        return result if result else await get_klines_sdk(self.client, self.config.SYMBOL, self.config.INTERVAL)

    async def get_balances(self):
        """Fetch balances, preferring HTTP."""
        result = await get_balance_http(self.config)
        return result if result else await get_balance_sdk(self.client)

    async def place_order(self, symbol: str, side: str, quantity: float, price: float):
        """Place order, preferring HTTP."""
        result = await place_order_http(self.config, symbol, side, quantity, price)
        return result if result else await place_order_sdk(self.client, symbol, side, quantity, price)

    async def query_open_orders(self, symbol: str):
        """Query open orders, preferring HTTP."""
        result = await query_open_orders_http(self.config, symbol)
        return result if result else await query_open_orders_sdk(self.client, symbol)

    async def cancel_order(self, symbol: str, order_id: str):
        """Cancel order, preferring HTTP."""
        result = await cancel_order_http(self.config, symbol, order_id)
        return result if result else await cancel_order_sdk(self.client, symbol, order_id)
