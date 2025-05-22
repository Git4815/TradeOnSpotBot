import logging
from pathlib import Path
import json
from strategies.feeder import Feeder
from config import Config

logger = logging.getLogger(__name__)

async def manage_orders(strategy, feeder: Feeder, config: Config, dynamic_dir: Path):
    """Manage orders for low spread strategy (max 1 order)."""
    try:
        open_orders = await feeder.query_open_orders(config.SYMBOL)
        balances = await feeder.get_balances()
        available_usdt = balances.get("USDT", 0)

        open_value = sum(float(o["quantity"]) * float(o["price"]) for o in open_orders if o["side"] == "buy")
        total_usdt = available_usdt + open_value

        desired_order = {"side": "buy", "quantity": total_usdt / 1.0, "price": 1.0}

        if len(open_orders) > 1:
            logger.info("Max 1 order reached, canceling excess")
            for order in open_orders[1:]:
                await feeder.cancel_order(config.SYMBOL, order["order_id"])
            open_orders = open_orders[:1]

        if not open_orders or float(open_orders[0]["quantity"]) != desired_order["quantity"]:
            logger.info("Mismatched order, canceling")
            for order in open_orders:
                await feeder.cancel_order(config.SYMBOL, order["order_id"])
            open_orders = []
            available_usdt = (await feeder.get_balances()).get("USDT", 0)
            if desired_order["quantity"] <= available_usdt:
                order_id = await feeder.place_order(config.SYMBOL, desired_order["side"], desired_order["quantity"], desired_order["price"])
                if order_id:
                    open_orders = [{"order_id": order_id, "side": desired_order["side"], "quantity": desired_order["quantity"], "price": desired_order["price"]}]
                    logger.info(f"Placed order: {desired_order}")
                else:
                    open_orders = []
                    logger.warning(f"Failed to place order: {desired_order}")
            else:
                logger.warning(f"Insufficient USDT for order: {desired_order['quantity']}")

        order_log = dynamic_dir / "order_log.json"
        order_log.parent.mkdir(parents=True, exist_ok=True)
        with order_log.open("w") as f:
            json.dump({"open_orders": open_orders}, f, indent=2)
        logger.info(f"Order log saved: {order_log}")
        return True
    except Exception as e:
        logger.error(f"Error in manage_orders: {e}")
        return False
