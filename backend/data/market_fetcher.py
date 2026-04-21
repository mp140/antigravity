"""
ANTIGRAVITY v3.0 — Market Data Fetcher
Multi-source market data with caching layer.
Primary: Yahoo Finance (free, unlimited)
"""
import yfinance as yf
import pandas as pd
import numpy as np
import time
import threading
from typing import Optional
from backend.utils import get_logger, fmt_price, fmt_pct, fmt_volume

log = get_logger("MarketFetcher")

# ─── In-memory cache ─────────────────────────────────────────────────────
_cache: dict = {}
_cache_ttl: dict = {}
CACHE_DURATION = 30  # seconds


def _is_cached(key: str) -> bool:
    return key in _cache and time.time() - _cache_ttl.get(key, 0) < CACHE_DURATION


def _set_cache(key: str, data):
    _cache[key] = data
    _cache_ttl[key] = time.time()


# ─── Core fetcher ─────────────────────────────────────────────────────────
def get_stock_data(ticker: str, period: str = "6mo", interval: str = "1d") -> Optional[pd.DataFrame]:
    """Fetch OHLCV data from Yahoo Finance with caching."""
    cache_key = f"{ticker}_{period}_{interval}"
    if _is_cached(cache_key):
        return _cache[cache_key]
    try:
        tk = yf.Ticker(ticker)
        df = tk.history(period=period, interval=interval)
        if df.empty:
            log.warning(f"No data for {ticker}")
            return None
        _set_cache(cache_key, df)
        return df
    except Exception as e:
        log.error(f"Failed to fetch {ticker}: {e}")
        return None


def get_current_price(ticker: str) -> dict:
    """Get real-time price snapshot for a ticker."""
    cache_key = f"price_{ticker}"
    if _is_cached(cache_key):
        return _cache[cache_key]
    try:
        tk = yf.Ticker(ticker)
        info = tk.fast_info
        hist = tk.history(period="2d", interval="1d")
        if hist.empty:
            return {"error": f"No data for {ticker}"}

        current = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else current
        change = current - prev
        change_pct = (change / prev * 100) if prev != 0 else 0
        volume = int(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0

        result = {
            "ticker": ticker,
            "price": round(current, 4),
            "change": round(change, 4),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "high": round(float(hist["High"].iloc[-1]), 4),
            "low": round(float(hist["Low"].iloc[-1]), 4),
            "open": round(float(hist["Open"].iloc[-1]), 4),
            "prev_close": round(prev, 4),
            "market_cap": getattr(info, "market_cap", None),
            "formatted": {
                "price": fmt_price(current),
                "change": fmt_price(change),
                "change_pct": fmt_pct(change_pct),
                "volume": fmt_volume(volume),
            }
        }
        _set_cache(cache_key, result)
        return result
    except Exception as e:
        log.error(f"Price fetch failed for {ticker}: {e}")
        return {"ticker": ticker, "error": str(e)}


def get_multi_prices(tickers: list) -> list:
    """Fetch prices for multiple tickers concurrently."""
    results = []
    lock = threading.Lock()

    def _fetch(t):
        data = get_current_price(t)
        with lock:
            results.append(data)

    threads = [threading.Thread(target=_fetch, args=(t,)) for t in tickers]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)

    return sorted(results, key=lambda x: abs(x.get("change_pct", 0)), reverse=True)


def get_ticker_info(ticker: str) -> dict:
    """Get extended ticker information."""
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        return {
            "name": info.get("shortName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "dividend_yield": info.get("dividendYield"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "avg_volume": info.get("averageVolume"),
            "beta": info.get("beta"),
        }
    except Exception as e:
        log.error(f"Info fetch failed for {ticker}: {e}")
        return {"name": ticker}
