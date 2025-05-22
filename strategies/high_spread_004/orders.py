import logging
from pathlib import Path
import json
from strategies.feeder import Feeder
from config import Config

logger = logging.getLogger(__name__)

async def manage_orders(strategy, feeder: Feeder, config: Config, dynamic_dir: Path):
    """Manage orders for high spread strategy (max 3 orders)."""
    try:
        open_orders = await feeder.query_open_orders(config.SYMBOL)
        balances = await feeder.get_balances()
        available_usdt = balances.get("USDT", 0)

        open_value = sum(float(o["quantity"]) * float(o["price"]) for o in open_orders if o["side"] == "buy")
        total_usdt = available_usdt + open_value

        desired_orders = [
            {"side": "buy", "quantity": total_usdt * 0.5 / 1.0, "price": 1.0},
            {"side": "buy", "quantity": total_usdt / 1.0, "price": 1.0}
        ]

        if len(open_orders) > 3:
            logger.info("Max 3 orders reached, canceling excess")
            for order in open_orders[3:]:
                await feeder.cancel_order(config.SYMBOL, order["order_id"])
            open_orders = open_orders[:3]

        current_quantities = sorted([float(o["quantity"]) for o in open_orders if o["side"] == "buy"])
        desired_quantities = sorted([d["quantity"] for d in desired_orders[:3]])

        if current_quantities != desired_quantities:
            logger.info("Mismatched orders, canceling all")
            for order in open_orders:
                await feeder.cancel_order(config.SYMBOL, order["order_id"])
            open_orders = []
            available_usdt = (await feeder.get_balances()).get("USDT", 0)
            for order in desired_orders[:3]:
                if order["quantity"] <= available_usdt:
                    order_id = await feeder.place_order(config.SYMBOL, order["side"], order["quantity"], order["price"])
                    if order_id:
                        open_orders.append({"order_id": order_id, "side": order["side"], "quantity": order["quantity"], "price": order["price"]})
                        available_usdt -= order["quantity"]
                        logger.info(f"Placed order: {order}")
                    else:
                        logger.warning(f"Failed to place order: {order}")
                else:
                    logger.warning(f"Insufficient USDT for order: {order['quantity']}")

        order_log = dynamic_dir / "order_log.json"
        order_log.parent.mkdir(parents=True, exist_ok=True)
        with order_log.open("w") as f:
            json.dump({"open_orders": open_orders}, f, indent=2)
        logger.info(f"Order log saved: {order_log}")
        return True
    except Exception as e:
        logger.error(f"Error in manage_orders: {e}")
        return False
