"""
ANTIGRAVITY v3.0 — Candlestick Pattern AI Agent
Pattern recognition with momentum shift detection.
"""
from backend.data.market_fetcher import get_stock_data
from backend.analysis.patterns import detect_patterns
from backend.utils import get_logger

log = get_logger("Agent:Candlestick")


class CandlestickAgent:
    """Pattern Recognition AI — candlestick patterns and momentum shifts."""

    def analyze(self, ticker: str) -> dict:
        log.info(f"Pattern analysis: {ticker}")
        df = get_stock_data(ticker, period="3mo", interval="1d")
        if df is None:
            return {"ticker": ticker, "error": "No data", "score": 50}

        result = detect_patterns(df)
        patterns = result.get("patterns", [])

        # Score based on patterns
        bullish = result.get("bullish_count", 0)
        bearish = result.get("bearish_count", 0)

        if bullish > bearish:
            score = min(90, 60 + bullish * 10)
            bias = "bullish"
        elif bearish > bullish:
            score = max(10, 40 - bearish * 10)
            bias = "bearish"
        else:
            score = 50
            bias = "neutral"

        output = {
            "ticker": ticker,
            "score": score,
            "bias": bias,
            "patterns": patterns,
            "pattern_count": len(patterns),
            "summary": result.get("summary", "neutral"),
            "avg_confidence": result.get("avg_confidence", 50),
        }
        log.info(f"{ticker}: {len(patterns)} patterns detected, bias={bias}")
        return output
