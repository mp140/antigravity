"""
ANTIGRAVITY v3.0 — News Fetcher
RSS-based news aggregation with optional NewsAPI.
"""
import feedparser
import requests
import time
import re
from typing import List
from backend.utils import get_logger, now_iso
from backend.config.settings import NEWS_API_KEY

log = get_logger("NewsFetcher")

# ─── RSS Sources ──────────────────────────────────────────────────────────
RSS_FEEDS = {
    "google_finance": "https://news.google.com/rss/search?q=stock+market&hl=en-US&gl=US&ceid=US:en",
    "yahoo_finance": "https://finance.yahoo.com/news/rssindex",
    "cnbc": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "reuters_business": "https://www.rss.reuters.com/news/businessNews",
    "marketwatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
}

_news_cache: dict = {}
_news_cache_time: dict = {}
NEWS_CACHE_TTL = 120  # 2 minutes


def fetch_rss_news(ticker: str = "") -> List[dict]:
    """Fetch news from RSS feeds, optionally filtered by ticker."""
    cache_key = f"rss_{ticker}"
    if cache_key in _news_cache and time.time() - _news_cache_time.get(cache_key, 0) < NEWS_CACHE_TTL:
        return _news_cache[cache_key]

    articles = []
    import urllib.parse
    query = ticker if ticker else "stock market"
    encoded_query = urllib.parse.quote(f"{query} stock")
    google_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    try:
        feed = feedparser.parse(google_url)
        for entry in feed.entries[:15]:
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "source": _extract_source(entry.get("title", "")),
                "ticker": ticker.upper() if ticker else "MARKET",
            })
    except Exception as e:
        log.error(f"RSS fetch error: {e}")

    # Also fetch from general feeds
    if not ticker:
        for name, url in list(RSS_FEEDS.items())[:3]:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:
                    articles.append({
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "source": name.replace("_", " ").title(),
                        "ticker": "MARKET",
                    })
            except Exception:
                continue

    _news_cache[cache_key] = articles
    _news_cache_time[cache_key] = time.time()
    return articles


def fetch_newsapi(ticker: str = "", limit: int = 10) -> List[dict]:
    """Fetch from NewsAPI (requires API key)."""
    if not NEWS_API_KEY:
        return []
    try:
        query = f"{ticker} stock" if ticker else "stock market finance"
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={"q": query, "sortBy": "publishedAt", "pageSize": limit, "apiKey": NEWS_API_KEY},
            timeout=10,
        )
        data = resp.json()
        return [
            {
                "title": a.get("title", ""),
                "link": a.get("url", ""),
                "published": a.get("publishedAt", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
                "description": a.get("description", ""),
                "ticker": ticker.upper() if ticker else "MARKET",
            }
            for a in data.get("articles", [])
        ]
    except Exception as e:
        log.error(f"NewsAPI error: {e}")
        return []


def get_all_news(ticker: str = "") -> List[dict]:
    """Aggregate news from all available sources."""
    news = fetch_rss_news(ticker)
    if NEWS_API_KEY:
        news.extend(fetch_newsapi(ticker))
    # Deduplicate by title similarity
    seen_titles = set()
    unique = []
    for article in news:
        title_key = re.sub(r'[^a-z0-9]', '', article["title"].lower())[:50]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique.append(article)
    return unique[:25]


def _extract_source(title: str) -> str:
    if " - " in title:
        return title.split(" - ")[-1].strip()
    return "Google News"
