import logging
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MinuteLocator
from telegram import Bot
from datetime import datetime
import time
from pathlib import Path
import io
import numpy as np
from PIL import Image
import shutil
import pandas as pd
from mexc_sdk import Spot

logger = logging.getLogger(__name__)

def fetch_orders(client):
    """Fetch open and executed orders from MEXC SDK (synchronous)."""
    try:
        symbol = "USD1USDT"  # Default symbol

        # Fetch open orders (synchronous method)
        open_orders = client.open_orders(symbol)  # No 'await' needed
        open_orders_list = [
            {
                "price": float(order["price"]),
                "side": "buy" if order["side"] == "BUY" else "sell",
                "timestamp": order.get("time", int(time.time() * 1000))
            }
            for order in open_orders
        ]

        # Fetch executed orders (trade history, synchronous method)
        trades = client.account_trade_list(symbol, limit=100)  # No 'await' needed
        executed_orders = [
            {
                "price": float(trade["price"]),
                "side": "buy" if trade["isBuyer"] else "sell",
                "timestamp": trade["time"],
                "quantity": float(trade["qty"])
            }
            for trade in trades
        ]

        return open_orders_list, executed_orders
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return [], []

async def generate_and_send_plot(feeder, config, dynamic_dir: Path):
    """Generate OHLC candlestick chart with volume and order markers."""
    klines_result = await feeder.get_klines()
    if not klines_result or "timestamp" not in klines_result or not klines_result["klines"]:
        logger.error("No valid Klines data for plotting")
        return

    # Prepare data for candlestick chart
    data = []
    for kline in klines_result["klines"]:
        if len(kline) >= 7:  # Ensure kline has required fields
            try:
                data.append({
                    "time": datetime.fromtimestamp(kline[0] / 1000),
                    "open": float(kline[1]),
                    "high": float(kline[2]),
                    "low": float(kline[3]),
                    "close": float(kline[4]),
                    "volume": float(kline[5])
                })
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid kline data: {kline}, error: {e}")
                continue
    if len(data) < 2:
        logger.error(f"Insufficient kline data points: {len(data)}")
        return
    df = pd.DataFrame(data)
    logger.info(f"Plotting {len(df)} klines from {df['time'].min()} to {df['time'].max()}")

    # Validate volume data
    if df["volume"].isnull().any() or (df["volume"] <= 0).all():
        logger.warning("Volume data is invalid or all zeros, volume bars may not appear")
    else:
        logger.info(f"Volume range: {df['volume'].min()} to {df['volume'].max()}")

    # Create MEXC SDK client using config attributes
    client = Spot(api_key=config.API_KEY, api_secret=config.API_SECRET)
    open_orders, executed_orders = fetch_orders(client)  # Synchronous call

    # Set up dark theme
    plt.style.use("dark_background")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

    # Candlestick chart (make candles 3x thicker)
    width = 0.0001  # Base width for open/close ticks
    for idx, row in df.iterrows():
        color = "green" if row["close"] >= row["open"] else "red"
        # Body (3x thicker: linewidth from 2 to 6)
        ax1.plot([row["time"], row["time"]], [row["open"], row["close"]], color=color, linewidth=6)
        # Wicks
        ax1.plot([row["time"], row["time"]], [row["low"], row["high"]], color=color, linewidth=1)
        # Open/Close ticks (adjust width proportionally: 0.0001 to 0.0003)
        ax1.plot([row["time"], row["time"] - pd.Timedelta(seconds=width * 3)], [row["open"], row["open"]], color=color, linewidth=1)
        ax1.plot([row["time"], row["time"] + pd.Timedelta(seconds=width * 3)], [row["close"], row["close"]], color=color, linewidth=1)

    # Volume bars (set width to span ~80% of a 1-minute interval)
    bar_width = 0.0002  # Adjusted width for visibility (in fraction of time axis)
    ax2.bar(df["time"], df["volume"], width=bar_width, color="gray", alpha=0.5)

    # Set price padding (1 tick = 0.0001 USD1)
    tick = 0.0001
    price_min = df["low"].min() - tick
    price_max = df["high"].max() + tick
    ax1.set_ylim(price_min, price_max)

    # Set volume axis limits to ensure visibility
    if df["volume"].max() > 0:
        ax2.set_ylim(0, df["volume"].max() * 1.1)  # Add 10% padding above max volume
    else:
        ax2.set_ylim(0, 1)  # Default range if no volume

    # Plot open orders
    for order in open_orders:
        color = "green" if order["side"] == "buy" else "red"
        ax1.axhline(y=order["price"], color=color, linestyle="--", linewidth=4, alpha=0.7)

    # Plot executed orders
    tick_offset = tick / 2  # 0.00005 USD1
    for order in executed_orders:
        order_time = datetime.fromtimestamp(order["timestamp"] / 1000)
        # Find candle with matching timestamp
        candle = df[df["time"].dt.floor("min") == order_time.replace(second=0, microsecond=0)]
        if not candle.empty:
            candle = candle.iloc[0]
            if order["side"] == "sell":
                # Red downward triangle above high
                ax1.plot(order_time, candle["high"] + tick_offset, marker="v", color="red", markersize=10)
            else:
                # Green upward triangle below low
                ax1.plot(order_time, candle["low"] - tick_offset, marker="^", color="green", markersize=10)

    # X-axis: 5-minute markings, limit to 50-minute span
    ax1.set_xlim(df["time"].min(), df["time"].max())
    ax1.xaxis.set_major_locator(MinuteLocator(interval=5))
    ax1.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    plt.xticks(rotation=45)

    # Styling
    ax1.set_title(f"OHLC Candlestick Chart for {klines_result['klines'][0][-1]}", color="white")
    ax1.set_ylabel("Price (USD1)", color="white")
    ax2.set_ylabel("Volume", color="white")
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax2.grid(True, linestyle="--", alpha=0.3)
    ax1.tick_params(colors="white")
    ax2.tick_params(colors="white")
    fig.patch.set_facecolor("#1c2526")
    ax1.set_facecolor("#2a2e39")
    ax2.set_facecolor("#2a2e39")

    # Adjust layout
    plt.tight_layout()

    # Save plot
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", facecolor=fig.get_facecolor())
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
