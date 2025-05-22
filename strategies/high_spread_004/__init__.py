import logging
from config import Config
from .orders import manage_orders

logger = logging.getLogger(__name__)

class HighSpreadStrategy:
    def __init__(self, config: Config):
        self.config = config

    async def manage_orders(self, feeder, config, dynamic_dir):
        """Manage orders for high spread strategy."""
        try:
            return await manage_orders(self, feeder, config, dynamic_dir)
        except Exception as e:
            logger.error(f"HighSpreadStrategy: Error in manage_orders: {e}")
            raise
