"""
ANTIGRAVITY v3.0 — Master Brain Decision Engine
Orchestrates all agents into a unified trading decision.
"""
import time
from backend.agents.director import DirectorAgent
from backend.agents.quant import QuantAgent
from backend.agents.candlestick import CandlestickAgent
from backend.agents.sentiment import SentimentAgent
from backend.agents.risk_manager import RiskManagerAgent
from backend.config.settings import WEIGHT_TECHNICAL, WEIGHT_AI_PREDICTION, WEIGHT_SENTIMENT, WEIGHT_PATTERN
from backend.utils import get_logger, now_iso

log = get_logger("MasterBrain")


class MasterBrain:
    """Core Decision Engine — weighted combination of all agent signals."""

    def __init__(self):
        self.director = DirectorAgent()
        self.quant = QuantAgent()
        self.candlestick = CandlestickAgent()
        self.sentiment_agent = SentimentAgent()
        self.risk_manager = RiskManagerAgent()

    def full_analysis(self, ticker: str) -> dict:
        """Run all agents and produce a unified decision."""
        start = time.time()
        log.info(f"═══ Full Analysis: {ticker} ═══")

        # 1. Macro regime
        macro = self.director.analyze()

        # 2. Technical analysis
        technical = self.quant.analyze(ticker)

        # 3. Pattern recognition
        patterns = self.candlestick.analyze(ticker)

        # 4. Sentiment
        sentiment = self.sentiment_agent.analyze(ticker)

        # 5. Weighted final score
        tech_score = technical.get("score", 50) / 100
        pattern_score = patterns.get("score", 50) / 100
        sent_score = sentiment.get("score", 50) / 100
        # Use tech score as proxy for AI prediction for now
        ai_score = tech_score

        final_score = (
            tech_score * WEIGHT_TECHNICAL +
            ai_score * WEIGHT_AI_PREDICTION +
            sent_score * WEIGHT_SENTIMENT +
            pattern_score * WEIGHT_PATTERN
        )

        # Apply macro regime modifier
        regime_mod = macro.get("regime_score", 0.6)
        adjusted_score = final_score * (0.5 + regime_mod * 0.5)

        # Decision
        confidence = int(adjusted_score * 100)
        if adjusted_score >= 0.70:
            action = "BUY"
            direction = "long"
        elif adjusted_score <= 0.30:
            action = "SELL"
            direction = "short"
        else:
            action = "HOLD"
            direction = "none"

        # 6. Risk assessment (only if actionable)
        risk = {}
        if action in ("BUY", "SELL"):
            risk = self.risk_manager.analyze(ticker, confidence, direction)
            if not risk.get("approved", False):
                action = "HOLD"

        elapsed = round(time.time() - start, 2)

        result = {
            "ticker": ticker,
            "action": action,
            "confidence": confidence,
            "final_score": round(adjusted_score, 4),
            "timestamp": now_iso(),
            "elapsed_seconds": elapsed,
            "macro": {
                "regime": macro.get("regime"),
                "regime_score": macro.get("regime_score"),
                "vix": macro.get("vix"),
                "recommendation": macro.get("recommendation"),
            },
            "technical": {
                "score": technical.get("score"),
                "action": technical.get("action"),
                "trend": technical.get("trend"),
                "signals": technical.get("signals", [])[:5],
                "key_levels": technical.get("key_levels", {}),
            },
            "patterns": {
                "score": patterns.get("score"),
                "bias": patterns.get("bias"),
                "patterns": patterns.get("patterns", [])[:3],
            },
            "sentiment": {
                "score": sentiment.get("score"),
                "label": sentiment.get("label"),
                "news_count": sentiment.get("news_count"),
                "top_headlines": sentiment.get("top_headlines", [])[:3],
            },
            "risk": risk,
            "agent_weights": {
                "technical": WEIGHT_TECHNICAL,
                "ai_prediction": WEIGHT_AI_PREDICTION,
                "sentiment": WEIGHT_SENTIMENT,
                "pattern": WEIGHT_PATTERN,
            },
        }

        log.info(f"═══ {ticker}: {action} (confidence={confidence}%, score={adjusted_score:.3f}) [{elapsed}s] ═══")
        return result

    def quick_scan(self, ticker: str) -> dict:
        """Lightweight scan — technical only, for batch processing."""
        technical = self.quant.analyze(ticker)
        score = technical.get("score", 50)
        return {
            "ticker": ticker,
            "score": score,
            "trend": technical.get("trend", "neutral"),
            "action": technical.get("action", "HOLD"),
            "key_levels": technical.get("key_levels", {}),
        }
