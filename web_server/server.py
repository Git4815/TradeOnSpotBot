from flask import Flask, render_template, send_from_directory
from datetime import datetime
import logging
import os
import time
from pathlib import Path
from config import Config

app = Flask(__name__, template_folder="templates", static_folder="static")
config = Config()

# Ensure logs/ directory exists
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(os.path.join(log_dir, "web_server.log")), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_latest_chart():
    """Find the latest chart."""
    dynamic_dirs = sorted(Path("logs/dynamic").glob("*"), key=lambda x: x.name, reverse=True)
    for d in dynamic_dirs:
        chart_path = d / "kline_plot.png"
        if chart_path.exists():
            return str(chart_path)  # Return absolute path
    return None

@app.route("/logs/<path:filename>")
def serve_logs(filename):
    """Serve files from logs/ directory."""
    return send_from_directory("logs", filename)

@app.route("/")
def index():
    """Render the dashboard."""
    chart_path = get_latest_chart()
    chart_url = f"/logs/{chart_path[len('logs/'):]}" if chart_path else None
    system_status = f"Telegram Ban Until: {datetime.fromtimestamp(config.TELEGRAM_BAN) if config.TELEGRAM_BAN > time.time() else 'Not banned'}"
    return render_template(
        "index.html",
        chart_path=chart_url,
        system_status=system_status,
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
