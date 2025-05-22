import logging
from pathlib import Path
from config import Config
from strategies.high_spread_004 import HighSpreadStrategy
from strategies.low_spread_001 import LowSpreadStrategy

logger = logging.getLogger(__name__)

class Scanner:
    def __init__(self, config: Config):
        self.config = config
        self.strategies = []

    async def initialize_strategies(self):
        """Initialize trading strategies."""
        try:
            self.strategies = [HighSpreadStrategy(self.config), LowSpreadStrategy(self.config)]
            logger.info("Strategies initialized: high_spread_004, low_spread_001")
        except Exception as e:
            logger.error(f"Error initializing strategies: {e}")

    async def select_strategy(self, klines_file: str):
        """Select strategy based on spread."""
        try:
            with open(klines_file, "r") as f:
                klines = [line.strip().split(",") for line in f.readlines()]

            if not klines:
                logger.warning("No Klines data available")
                return None

            latest_kline = klines[-1]
            high, low = float(latest_kline[2]), float(latest_kline[3])
            spread = (high - low) / low * 100

            if spread > 0.5:
                logger.info("High spread detected, selecting high_spread_004")
                return self.strategies[0]  # HighSpreadStrategy
            elif spread <= 0.5:
                logger.info("Low spread detected, selecting low_spread_001")
                return self.strategies[1]  # LowSpreadStrategy
            logger.info("No suitable strategy found")
            return None
        except Exception as e:
            logger.error(f"Error selecting strategy: {e}")
            return None
