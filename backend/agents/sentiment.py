"""
ANTIGRAVITY v3.0 — Sentiment Agent
Aggregates news + social sentiment into a unified signal.
"""
from backend.data.news_fetcher import get_all_news
from backend.data.sentiment_engine import analyze_news_for_ticker
from backend.utils import get_logger

log = get_logger("Agent:Sentiment")


class SentimentAgent:
    """Sentiment Analyst — news and social media sentiment aggregation."""

    def analyze(self, ticker: str) -> dict:
        log.info(f"Sentiment analysis: {ticker}")
        news = get_all_news(ticker)

        if not news:
            return {"ticker": ticker, "score": 50, "label": "neutral", "news_count": 0}

        sentiment = analyze_news_for_ticker(news)

        # Convert sentiment score (-1 to 1) to our 0-100 scale
        raw_score = sentiment.get("aggregate_score", 0)
        score = int((raw_score + 1) * 50)  # Map -1..1 to 0..100
        score = max(0, min(100, score))

        output = {
            "ticker": ticker,
            "score": score,
            "label": sentiment.get("label", "neutral"),
            "aggregate_score": raw_score,
            "confidence": sentiment.get("confidence", 0),
            "news_count": len(news),
            "bullish_count": sentiment.get("bullish_count", 0),
            "bearish_count": sentiment.get("bearish_count", 0),
            "top_headlines": [
                {"title": n.get("title", ""), "source": n.get("source", "")}
                for n in news[:5]
            ],
            "details": sentiment.get("details", [])[:5],
        }
        log.info(f"{ticker}: Sentiment={sentiment.get('label')} Score={score}")
        return output
