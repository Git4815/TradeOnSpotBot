import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

async def generate_and_send_plot(klines, config, dynamic_dir: Path, open_orders, executed_trades):
    try:
        klines_data = klines.get("klines", [])
        try:
            with open("strategies/klines_latest/klines_latest.json", "r") as f:
                klines_data = json.load(f).get("klines", klines_data)
        except Exception as e:
            logger.warning(f"Failed to load klines_latest.json: {e}")

        open_orders_data = open_orders
        try:
            with open("strategies/orders/open_orders.json", "r") as f:
                open_orders_data = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load open_orders.json: {e}")

        executed_trades_data = executed_trades
        try:
            with open("strategies/orders/order_regs.json", "r") as f:
                executed_trades_data = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load order_regs.json: {e}")

        if not klines_data:
            logger.error("No Klines data available")
            return None

        # Validate Klines data
        valid_klines = [k for k in klines_data if len(k) >= 11]
        if not valid_klines:
            logger.error("No valid Klines data after filtering")
            return None

        df = pd.DataFrame(
            valid_klines,
            columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)

        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.03, subplot_titles=("", ""),
            row_heights=[0.7, 0.3]
        )

        fig.add_trace(
            go.Candlestick(
                x=df["timestamp"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="Klines"
            ),
            row=1, col=1
        )

        colors = ['green' if row['close'] >= row['open'] else 'red' for _, row in df.iterrows()]
        fig.add_trace(
            go.Bar(
                x=df["timestamp"],
                y=df["volume"],
                marker_color=colors,
                name="Volume"
            ),
            row=2, col=1
        )

        for order in open_orders_data:
            price = float(order["price"])
            quantity = float(order["quantity"])
            side = order["side"]
            color = "red" if side == "sell" else "green"
            fig.add_trace(
                go.Scatter(
                    x=[df["timestamp"].iloc[0], df["timestamp"].iloc[-1]],
                    y=[price, price],
                    mode="lines",
                    line=dict(color=color, dash="dash", width=4),
                    name=f"{side.capitalize()} Order",
                    showlegend=False
                ),
                row=1, col=1
            )
            fig.add_annotation(
                x=df["timestamp"].iloc[-1],
                y=price,
                text=f"{side.capitalize()} {price:.4f} ({quantity:.2f})",
                showarrow=False,
                font=dict(color="white", size=10),
                bgcolor="black",
                bordercolor="black",
                borderwidth=1,
                xshift=10
            )
            fig.add_trace(
                go.Scatter(
                    x=[df["timestamp"].iloc[-1]],
                    y=[price + 0.00005 if side == "buy" else price - 0.00005],
                    mode="markers",
                    marker=dict(symbol="triangle-up" if side == "buy" else "triangle-down", size=10, color=color),
                    showlegend=False
                ),
                row=1, col=1
            )

        for trade in executed_trades_data:
            price = float(trade["price"])
            side = trade["side"]
            color = "red" if side == "sell" else "green"
            timestamp = pd.to_datetime(trade["timestamp"], unit="ms")
            fig.add_trace(
                go.Scatter(
                    x=[timestamp],
                    y=[price + 0.00005 if side == "buy" else price - 0.00005],
                    mode="markers",
                    marker=dict(symbol="triangle-up" if side == "buy" else "triangle-down", size=10, color=color),
                    name=f"{side.capitalize()} Trade",
                    showlegend=False
                ),
                row=1, col=1
            )

        fig.update_layout(
            title=f"{config.SYMBOL} Klines",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
            showlegend=False,
            height=800,
            margin=dict(l=50, r=50, t=50, b=50),
            template="plotly_dark"
        )
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

        chart_path = dynamic_dir / "kline_plot.html"
        fig.write_html(chart_path, full_html=True)
        logger.info(f"Chart saved to {chart_path}")

        png_path = dynamic_dir / "kline_plot.png"
        try:
            from weasyprint import HTML
            HTML(str(chart_path)).write_png(str(png_path))
            logger.debug(f"PNG saved to {png_path}")
            return str(png_path)
        except Exception as e:
            logger.warning(f"Failed to save PNG: {e}")
            # Fallback to kaleido
            try:
                import kaleido
                fig.write_image("png", file=str(png_path))
                logger.debug(f"PNG saved to {png_path} using kaleido")
                return str(png_path)
            except Exception as e:
                logger.warning(f"Failed to save PNG with kaleido: {e}")
                return str(chart_path)
    except Exception as e:
        logger.error(f"Plot generation error: {e}", exc_info=True)
        return None
