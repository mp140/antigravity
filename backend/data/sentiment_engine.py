"""
ANTIGRAVITY v3.0 — Sentiment Engine
VADER-based headline sentiment with impact multiplier scoring.
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List
from backend.utils import get_logger

log = get_logger("SentimentEngine")

_analyzer = SentimentIntensityAnalyzer()

# ─── Impact keywords that amplify sentiment ──────────────────────────────
HIGH_IMPACT_KEYWORDS = {
    "positive": ["surge", "soar", "breakout", "beat expectations", "upgrade", "record high",
                 "strong earnings", "bullish", "outperform", "rally", "catalyst", "growth"],
    "negative": ["crash", "plunge", "miss", "downgrade", "lawsuit", "bankruptcy", "fraud",
                 "recession", "bearish", "sell-off", "investigation", "default", "warning"],
    "neutral_dampeners": ["might", "could", "possibly", "uncertain", "mixed", "flat"],
}


def analyze_headline(text: str) -> dict:
    """Analyze a single headline for sentiment."""
    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]

    # Apply impact multiplier
    text_lower = text.lower()
    multiplier = 1.0
    impact_level = "normal"

    for kw in HIGH_IMPACT_KEYWORDS["positive"]:
        if kw in text_lower:
            multiplier = 1.5
            impact_level = "high"
            break
    for kw in HIGH_IMPACT_KEYWORDS["negative"]:
        if kw in text_lower:
            multiplier = 1.5
            impact_level = "high"
            break
    for kw in HIGH_IMPACT_KEYWORDS["neutral_dampeners"]:
        if kw in text_lower:
            multiplier = 0.7
            impact_level = "dampened"
            break

    adjusted = max(-1, min(1, compound * multiplier))

    if adjusted >= 0.3:
        label = "bullish"
    elif adjusted >= 0.05:
        label = "slightly_bullish"
    elif adjusted <= -0.3:
        label = "bearish"
    elif adjusted <= -0.05:
        label = "slightly_bearish"
    else:
        label = "neutral"

    return {
        "text": text[:120],
        "raw_score": round(compound, 4),
        "adjusted_score": round(adjusted, 4),
        "label": label,
        "impact": impact_level,
        "positive": round(scores["pos"], 3),
        "negative": round(scores["neg"], 3),
        "neutral": round(scores["neu"], 3),
    }


def analyze_batch(headlines: List[str]) -> dict:
    """Analyze multiple headlines and return aggregate sentiment."""
    if not headlines:
        return {"aggregate_score": 0, "label": "neutral", "count": 0, "details": []}

    details = [analyze_headline(h) for h in headlines]
    scores = [d["adjusted_score"] for d in details]
    avg_score = sum(scores) / len(scores)
    bullish_count = sum(1 for d in details if "bullish" in d["label"])
    bearish_count = sum(1 for d in details if "bearish" in d["label"])

    if avg_score >= 0.2:
        agg_label = "bullish"
    elif avg_score >= 0.05:
        agg_label = "slightly_bullish"
    elif avg_score <= -0.2:
        agg_label = "bearish"
    elif avg_score <= -0.05:
        agg_label = "slightly_bearish"
    else:
        agg_label = "neutral"

    return {
        "aggregate_score": round(avg_score, 4),
        "label": agg_label,
        "count": len(details),
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "confidence": round(abs(avg_score) * 100, 1),
        "details": details[:10],
    }


def analyze_news_for_ticker(news_articles: list) -> dict:
    """Analyze a list of news article dicts (with 'title' field) for sentiment."""
    headlines = [a.get("title", "") for a in news_articles if a.get("title")]
    result = analyze_batch(headlines)
    return result
