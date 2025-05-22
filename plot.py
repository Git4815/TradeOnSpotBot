import logging
import matplotlib.pyplot as plt
from telegram import Bot
from datetime import datetime
import time
from pathlib import Path
import io
import numpy as np
from PIL import Image
import shutil

logger = logging.getLogger(__name__)

async def generate_and_send_plot(feeder, config, dynamic_dir: Path):
    """Generate Klines plot and send to Telegram."""
    klines_result = await feeder.get_klines()
    if not klines_result or "timestamp" not in klines_result:
        logger.error("No valid Klines data for plotting")
        return

    timestamps = []
    closes = []
    for kline in klines_result["klines"]:
        timestamps.append(datetime.fromtimestamp(kline[0] / 1000))
        closes.append(float(kline[4]))

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, closes, label="Close Price")
    plt.title(f"Klines for {klines_result['klines'][0][-1]}")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    output_path = dynamic_dir / "kline_plot.png"
    Image.open(buffer).save(output_path)
    logger.info(f"Chart saved: {output_path}")

    # Copy to static folder for Flask
    static_path = Path("web_server/static/kline_plot.png")
    shutil.copy(output_path, static_path)
    logger.info(f"Chart copied to: {static_path}")

    if config.TELEGRAM_BAN > time.time():
        logger.info(f"Telegram banned, chart saved: {output_path}")
        return

    try:
        bot = Bot(token=config.TG_BOT_TOKEN)
        with open(output_path, "rb") as photo:
            await bot.send_photo(chat_id=config.TG_USER_ID, photo=photo)
        logger.info("Chart sent to Telegram")
    except Exception as e:
        if "429" in str(e) or "Flood control exceeded" in str(e):
            ban_duration = 16514  # ~4.5 hours
            config.TELEGRAM_BAN = int(time.time() + ban_duration)
            logger.warning(f"Telegram ban until {datetime.fromtimestamp(config.TELEGRAM_BAN)}")
        logger.error(f"Telegram chart error: {e}")
