"""
ANTIGRAVITY v3.0 — Quant Analyst Agent
Technical analysis confluence scoring + multi-timeframe analysis.
"""
from backend.data.market_fetcher import get_stock_data
from backend.analysis.indicators import compute_all_indicators
from backend.utils import get_logger

log = get_logger("Agent:Quant")


class QuantAgent:
    """Technical Analyst — indicator confluence and trend scoring."""

    def analyze(self, ticker: str) -> dict:
        log.info(f"Technical analysis: {ticker}")
        df = get_stock_data(ticker, period="6mo", interval="1d")
        if df is None:
            return {"ticker": ticker, "error": "No data", "score": 50}

        indicators = compute_all_indicators(df)
        if "error" in indicators:
            return {"ticker": ticker, "error": indicators["error"], "score": 50}

        # Compute confluence score
        signals = indicators.get("signals", [])
        bullish = sum(1 for s in signals if s.get("bias") == "bullish")
        bearish = sum(1 for s in signals if s.get("bias") == "bearish")
        total = bullish + bearish

        if total == 0:
            score = 50
        else:
            score = int((bullish / total) * 100)

        # Determine action
        if score >= 75:
            action = "STRONG_BUY"
        elif score >= 60:
            action = "BUY"
        elif score <= 25:
            action = "STRONG_SELL"
        elif score <= 40:
            action = "SELL"
        else:
            action = "HOLD"

        result = {
            "ticker": ticker,
            "score": score,
            "action": action,
            "trend": indicators["trend"],
            "strength": indicators["strength_score"],
            "signals": signals,
            "key_levels": {
                "support": indicators.get("support"),
                "resistance": indicators.get("resistance"),
                "current_price": indicators.get("current_price"),
            },
            "indicators": indicators.get("indicators", {}),
            "volume": indicators.get("volume", {}),
        }
        log.info(f"{ticker}: Score={score} Action={action} Trend={indicators['trend']}")
        return result
