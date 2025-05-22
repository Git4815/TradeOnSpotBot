from flask import Flask, render_template, send_file
import os
from datetime import datetime
import time
import logging
from pathlib import Path
import json
from config import Config

app = Flask(__name__, template_folder="templates", static_folder="static")
config = Config()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/web_server.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_latest_chart():
    """Find the latest chart."""
    try:
        dynamic_dirs = sorted(Path("logs/dynamic").glob("*"), key=lambda x: x.name, reverse=True)
        for d in dynamic_dirs:
            chart_path = d / "kline_plot.png"
            if chart_path.exists():
                logger.info(f"Found chart: {chart_path}")
                return str(chart_path.relative_to(Path("logs")))
        logger.warning("No chart found")
        return None
    except Exception as e:
        logger.error(f"Error finding chart: {e}")
        return None

def get_spread_status():
    """Get latest spread status."""
    try:
        dynamic_dirs = sorted(Path("logs/dynamic").glob("*"), key=lambda x: x.name, reverse=True)
        for d in dynamic_dirs:
            log_file = d / "high_spread_004.log"
            if log_file.exists():
                with log_file.open("r") as f:
                    lines = f.readlines()
                    for line in reversed(lines):
                        if "High spread detected" in line:
                            timestamp = line.split(" - ")[0]
                            return f"High Spread - {timestamp}"
        return "No spread status available"
    except Exception as e:
        logger.error(f"Error getting spread status: {e}")
        return "No spread status available"

def get_order_status():
    """Get latest order status."""
    try:
        dynamic_dirs = sorted(Path("logs/dynamic").glob("*"), key=lambda x: x.name, reverse=True)
        for d in dynamic_dirs:
            order_log = d / "order_log.json"
            if order_log.exists():
                with order_log.open("r") as f:
                    data = json.load(f)
                    if data.get("open_orders"):
                        return f"Open orders: {len(data['open_orders'])}"
                return "No open orders"
        return "No open orders"
    except Exception as e:
        logger.error(f"Error getting order status: {e}")
        return "Error retrieving order status"

def get_system_status():
    """Get Telegram ban status."""
    try:
        if config.TELEGRAM_BAN > time.time():
            return f"Telegram Ban Until: {datetime.fromtimestamp(config.TELEGRAM_BAN)}"
        return "Telegram Ban Until: Not banned"
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return "Error retrieving system status"

@app.route("/")
def index():
    """Render the dashboard."""
    chart_path = get_latest_chart()
    spread_status = get_spread_status()
    order_status = get_order_status()
    system_status = get_system_status()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template(
        "index.html",
        chart_path=chart_path,
        spread_status=spread_status,
        order_status=order_status,
        system_status=system_status,
        current_time=current_time
    )

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files from logs/."""
    try:
        file_path = os.path.join("logs", filename)
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return "File not found", 404
        logger.info(f"Serving static file: {file_path}")
        return send_file(file_path)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}")
        return "Error serving file", 404
