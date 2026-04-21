"""
ANTIGRAVITY v3.0 — CIO Director Agent
Sets macro thesis: Risk-On / Risk-Off / Neutral
Based on VIX, global market sentiment, sector rotation.
"""
from backend.data.market_fetcher import get_current_price, get_stock_data
from backend.data.news_fetcher import get_all_news
from backend.data.sentiment_engine import analyze_news_for_ticker
from backend.utils import get_logger

log = get_logger("Agent:Director")


class DirectorAgent:
    """Chief Investment Officer — sets the macro regime."""

    def analyze(self) -> dict:
        log.info("Generating macro thesis...")
        vix = self._get_vix()
        spy = get_current_price("SPY")
        qqq = get_current_price("QQQ")
        gold = get_current_price("GC=F")
        news = get_all_news()
        sentiment = analyze_news_for_ticker(news)

        # Determine regime
        vix_level = vix.get("price", 20) if isinstance(vix, dict) else 20
        spy_change = spy.get("change_pct", 0) if isinstance(spy, dict) else 0

        if vix_level > 30:
            regime = "RISK_OFF"
            regime_score = 0.2
        elif vix_level > 20:
            regime = "CAUTIOUS"
            regime_score = 0.5
        elif vix_level < 15 and spy_change > 0:
            regime = "RISK_ON"
            regime_score = 0.9
        else:
            regime = "NEUTRAL"
            regime_score = 0.6

        # Adjust for sentiment
        sent_score = sentiment.get("aggregate_score", 0)
        if sent_score > 0.2:
            regime_score = min(1.0, regime_score + 0.1)
        elif sent_score < -0.2:
            regime_score = max(0.0, regime_score - 0.1)

        thesis = {
            "regime": regime,
            "regime_score": round(regime_score, 2),
            "vix": round(vix_level, 2),
            "spy_change_pct": round(spy_change, 2),
            "market_sentiment": sentiment.get("label", "neutral"),
            "recommendation": self._recommendation(regime),
            "details": {
                "spy": spy.get("formatted", {}),
                "qqq": qqq.get("formatted", {}),
                "gold": gold.get("formatted", {}),
            },
        }
        log.info(f"Macro Thesis: {regime} (VIX: {vix_level:.1f})")
        return thesis

    def _get_vix(self) -> dict:
        try:
            return get_current_price("^VIX")
        except Exception:
            return {"price": 20}

    def _recommendation(self, regime: str) -> str:
        recs = {
            "RISK_ON": "Full exposure. Favour momentum plays, growth stocks, crypto. Increase position sizes.",
            "NEUTRAL": "Balanced approach. Mix value and growth. Standard position sizes.",
            "CAUTIOUS": "Reduce exposure. Favour value, dividends, hedges. Smaller position sizes.",
            "RISK_OFF": "Defensive mode. Gold, bonds, cash. Minimal new positions. Tighten stops.",
        }
        return recs.get(regime, recs["NEUTRAL"])
