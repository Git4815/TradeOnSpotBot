# TradeOnSpotBot
A trading bot for MEXC USD1USDT pair with Kline analysis, strategy selection, order management, chart generation, and a web dashboard.

## Setup
1. Clone the repo: `git clone https://github.com/yourusername/TradeOnSpotBot.git`
2. Install dependencies: `pip install mexc-sdk aiohttp python-telegram-bot matplotlib numpy pillow flask`
3. Update `config.py` with your MEXC API key, secret, Telegram token, and user ID.
4. Run: `python main.py`

## Features
- Fetches 1m Kline data for USD1USDT.
- Selects strategies based on spread (high_spread_004, low_spread_001).
- Manages orders with limits (3 for high spread, 1 for low spread).
- Sends charts to Telegram or saves for web display.
- Web dashboard at `http://localhost:5000`.
# TradeOnSpotBot
