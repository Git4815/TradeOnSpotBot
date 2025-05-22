import asyncio
import logging
from datetime import datetime
import time
from pathlib import Path
from strategies.scanner import Scanner
from strategies.feeder import Feeder
from plot import generate_and_send_plot
from config import Config
from web_server.server import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/main.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

config = Config()
scanner = Scanner(config)
feeder = Feeder(config)

async def send_message_to_telegram(message: str):
    """Send message to Telegram with ban handling."""
    from telegram import Bot
    try:
        bot = Bot(token=config.TG_BOT_TOKEN)
        await bot.send_message(chat_id=config.TG_USER_ID, text=message)
        logger.info("Message sent to Telegram")
    except Exception as e:
        if "429" in str(e) or "Flood control exceeded" in str(e):
            ban_duration = 16514  # ~4.5 hours
            config.TELEGRAM_BAN = int(time.time() + ban_duration)
            logger.warning(f"Telegram ban until {datetime.fromtimestamp(config.TELEGRAM_BAN)}")
        logger.error(f"Telegram message error: {e}")

async def main():
    """Main bot loop."""
    dynamic_dir = Path(f"logs/dynamic/{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    dynamic_dir.mkdir(parents=True, exist_ok=True)

    await scanner.initialize_strategies()
    await send_message_to_telegram("Bot started")

    # Start web server in a separate thread
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False), daemon=True).start()
    logger.info("Web server started at http://localhost:5000")

    while True:
        try:
            klines_result = await feeder.get_klines()
            if not klines_result or "timestamp" not in klines_result:
                logger.error("No valid Klines data")
                await asyncio.sleep(config.CHECK_INTERVAL)
                continue

            klines_file = Path(f"strategies/klines/Klines_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}")
            klines_file.parent.mkdir(parents=True, exist_ok=True)
            with klines_file.open("w") as f:
                for kline in klines_result["klines"]:
                    f.write(",".join(map(str, kline)) + "\n")

            selected_strategy = await scanner.select_strategy(str(klines_file))
            if selected_strategy:
                await selected_strategy.manage_orders(feeder, config, dynamic_dir)
            else:
                logger.info("No strategy selected")

            await generate_and_send_plot(feeder, config, dynamic_dir)
            await asyncio.sleep(config.CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            await asyncio.sleep(config.CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
