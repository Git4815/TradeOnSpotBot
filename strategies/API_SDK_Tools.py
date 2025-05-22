import logging
from mexc_sdk import Spot
import pkg_resources

logger = logging.getLogger(__name__)

# Log MEXC SDK version
try:
    sdk_version = pkg_resources.get_distribution("mexc-sdk").version
    logger.info(f"MEXC SDK version: {sdk_version}")
except Exception as e:
    logger.warning(f"Could not determine MEXC SDK version: {e}")

async def get_klines_sdk(client: Spot, symbol: str, interval: str, limit: int = 50):
    """Fetch Klines using SDK."""
    try:
        klines = client.klines(symbol=symbol, interval=interval, limit=limit)
        return {
            "timestamp": klines[0][0],
            "klines": [[
                k[0],  # time
                k[1],  # open
                k[2],  # high
                k[3],  # low
                k[4],  # close
                k[5],  # volume
                k[6],  # closeTime
                symbol
            ] for k in klines]
        }
    except Exception as e:
        logger.error(f"SDK Klines error: {e}")
        return None

async def get_balance_sdk(client: Spot, retries: int = 3, delay: float = 1.0):
    """Fetch account balances using SDK with retry logic."""
    import asyncio
    for attempt in range(retries):
        try:
            account = client.account_info()
            balances = account.get("balances", [])
            return {asset["asset"]: float(asset["free"]) for asset in balances if float(asset["free"]) > 0}
        except Exception as e:
            logger.error(f"SDK balance error (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
    logger.error("Failed to fetch balances after retries")
    return {}

async def place_order_sdk(client: Spot, symbol: str, side: str, quantity: float, price: float):
    """Place an order using SDK."""
    try:
        order = client.new_order(
            symbol=symbol,
            side="BUY" if side == "buy" else "SELL",
            order_type="LIMIT",
            quantity=quantity,  # Revert to quantity as per SDK inspection
            price=price
        )
        return order.get("orderId")
    except Exception as e:
        logger.error(f"SDK order error: {e}")
        return None

async def query_open_orders_sdk(client: Spot, symbol: str):
    """Query open orders using SDK."""
    try:
        orders = client.open_orders(symbol)
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
