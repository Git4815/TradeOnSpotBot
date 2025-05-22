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

        fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={"height_ratios": [3, 1]}, sharex=True, facecolor="#2E2E3A")
        ax.set_facecolor("#2E2E3A")
        ax2.set_facecolor("#2E2E3A")
        ax.grid(True, linestyle="-", linewidth=0.5, color="white")
        ax2.grid(True, linestyle="-", linewidth=0.5, color="white")

        candle_width = 0.4
        for i in range(len(klines)):
            color = "green" if closes[i] > opens[i] else "red"
            ax.add_patch(plt.Rectangle(
                (i - candle_width / 2, min(opens[i], closes[i])),
                candle_width,
                abs(opens[i] - closes[i]),
                facecolor=color,
                edgecolor="black"
            ))
            ax.plot([i, i], [lows[i], min(opens[i], closes[i])], color=color, linewidth=1)
            ax.plot([i, i], [max(opens[i], closes[i]), highs[i]], color=color, linewidth=1)
            ax2.bar(i, volumes[i], width=0.4, color=color)

        ax.set_xticks(range(0, len(timestamps), 5))
        ax.set_xticklabels([t.strftime("%Y-%m-%d %H:%M") for t in timestamps[::5]], rotation=45, color="white")
        ax.set_yticklabels([f"{y:.4f}" for y in ax.get_yticks()], color="white")
        ax2.set_yticklabels([f"{y:.2f}" for y in ax2.get_yticks()], color="white")
        ax.set_title(f"{klines[0][7]} - OHLC", color="white")
        ax.set_ylabel("Price (USDT)", color="white")
        ax2.set_ylabel("Volume (USD1)", color="white")

        plt.tight_layout()
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=150, facecolor="#2E2E3A")
        plt.close(fig)
        buffer.seek(0)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        Image.open(buffer).save(output_path, optimize=True, quality=95)
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
                    await bot.send_photo(chat_id=config.TG_USER_ID, photo=photo, caption="OHLC Chart")
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
