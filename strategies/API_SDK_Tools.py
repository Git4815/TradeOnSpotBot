import logging
from mexc_sdk import Spot

logger = logging.getLogger(__name__)

async def get_klines_sdk(client: Spot, symbol: str, interval: str, limit: int = 50):
    """Fetch Klines using SDK."""
    try:
        klines = client.get_kline(symbol, interval, limit=limit)
        return {
            "timestamp": klines[0]["time"],
            "klines": [[
                k["time"],
                k["open"],
                k["high"],
                k["low"],
                k["close"],
                k["volume"],
                k["closeTime"],
                symbol
            ] for k in klines]
        }
    except Exception as e:
        logger.error(f"SDK Klines error: {e}")
        return None

async def get_balance_sdk(client: Spot):
    """Fetch account balances using SDK."""
    try:
        account = client.get_account_info()
        balances = account.get("balances", [])
        return {asset["asset"]: float(asset["free"]) for asset in balances if float(asset["free"]) > 0}
    except Exception as e:
        logger.error(f"SDK balance error: {e}")
        return {}

async def place_order_sdk(client: Spot, symbol: str, side: str, quantity: float, price: float):
    """Place an order using SDK."""
    try:
        order = client.new_order(
            symbol=symbol,
            side="BUY" if side == "buy" else "SELL",
            order_type="LIMIT",
            quantity=quantity,
            price=price
        )
        return order.get("orderId")
    except Exception as e:
        logger.error(f"SDK order error: {e}")
        return None

async def query_open_orders_sdk(client: Spot, symbol: str):
    """Query open orders using SDK."""
    try:
        orders = client.get_open_orders(symbol)
        return [
            {
                "order_id": order["orderId"],
                "side": "buy" if order["side"] == "BUY" else "sell",
                "price": float(order["price"]),
                "quantity": float(order["origQty"])
            }
            for order in orders
        ]
    except Exception as e:
        logger.error(f"SDK open orders error: {e}")
        return []

async def cancel_order_sdk(client: Spot, symbol: str, order_id: str):
    """Cancel an order using SDK."""
    try:
        client.cancel_order(symbol, order_id)
        return True
    except Exception as e:
        if "-2011" in str(e):
            logger.info(f"Order {order_id} already canceled")
            return True
        logger.error(f"SDK cancel error: {e}")
        return False
