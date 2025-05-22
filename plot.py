import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from pathlib import Path
import io
from PIL import Image
import logging
import time
from strategies.feeder import Feeder
from config import Config
from telegram import Bot

logger = logging.getLogger(__name__)

async def generate_kline_plot(klines, output_path: Path):
    """Generate candlestick chart with volume."""
    try:
        timestamps = [datetime.fromtimestamp(int(k[0]) / 1000) for k in klines]
        opens = [float(k[1]) for k in klines]
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
        closes = [float(k[4]) for k in klines]
        volumes = [float(k[5]) for k in klines]

        fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
        ax.grid(True)
        ax2.bar(range(len(volumes)), volumes, color="blue")

        for i, (o, h, l, c) in enumerate(zip(opens, highs, lows, closes)):
            color = "green" if c > o else "red"
            ax.plot([i, i], [l, h], color=color)
            ax.plot([i - 0.2, i + 0.2], [o, o], color=color)
            ax.plot([i - 0.2, i + 0.2], [c, c], color=color)

        ax.set_xticks(range(0, len(timestamps), 5))
        ax.set_xticklabels([t.strftime("%H:%M") for t in timestamps[::5]], rotation=45)
        ax.set_title(f"{klines[0][7]} - OHLC")
        ax.set_ylabel("Price (USDT)")
        ax2.set_ylabel("Volume")

        plt.tight_layout()
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        plt.close(fig)
        buffer.seek(0)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        Image.open(buffer).save(output_path)
        logger.info(f"Chart saved: {output_path}")
        return str(output_path)
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        return None

async def generate_and_send_plot(feeder: Feeder, config: Config, dynamic_dir: Path):
    """Generate and send chart to Telegram or save for web."""
    try:
        klines_result = await feeder.get_klines()
        if not klines_result or "timestamp" not in klines_result:
            logger.error("No valid Klines for plotting")
            return

        klines = klines_result["klines"][-50:]
        output_path = dynamic_dir / "kline_plot.png"
        plot_path = await generate_kline_plot(klines, output_path)

        if plot_path and config.TELEGRAM_BAN <= time.time():
            try:
                bot = Bot(token=config.TG_BOT_TOKEN)
                with open(plot_path, "rb") as photo:
                    await bot.send_photo(chat_id=config.TG_USER_ID, photo=photo)
                logger.info("Chart sent to Telegram")
            except Exception as e:
                if "429" in str(e) or "Flood control exceeded" in str(e):
                    config.TELEGRAM_BAN = int(time.time() + 16514)
                    logger.warning(f"Telegram ban until {datetime.fromtimestamp(config.TELEGRAM_BAN)}")
                logger.error(f"Telegram chart error: {e}")
        elif plot_path:
            logger.info(f"Telegram banned, chart saved: {plot_path}")
    except Exception as e:
        logger.error(f"Error in generate_and_send_plot: {e}")
