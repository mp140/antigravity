"""
ANTIGRAVITY v3.0 — Unified FastAPI Server
All endpoints, background tasks, static file serving.
"""
import threading
import time
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.agents.master_brain import MasterBrain
from backend.ai.predictor import AIPredictor
from backend.data.market_fetcher import get_current_price, get_multi_prices, get_ticker_info
from backend.data.news_fetcher import get_all_news
from backend.data.sentiment_engine import analyze_news_for_ticker
from backend.execution.signal_generator import generate_signal, get_active_signals
from backend.portfolio.manager import PortfolioManager
from backend.portfolio.trade_journal import TradeJournal
from backend.agents.bot_agent import BotAgent
from backend.execution.etoro_broker import etoro_broker
from backend.constants import (
    STOCKS, CRYPTO, FOREX, COMMODITIES, ETFS, ASSET_CATEGORIES,
    TOP_25_WATCHLIST, PLATFORMS, COMMODITY_NAMES, ALL_TICKERS,
)
from backend.config.settings import TOP25_SCAN_INTERVAL, NEWS_REFRESH_INTERVAL
from backend.utils import get_logger, now_iso

log = get_logger("Server")

# ─── Init ─────────────────────────────────────────────────────────────────
app = FastAPI(title="ANTIGRAVITY v3.0", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

brain = MasterBrain()
predictor = AIPredictor()
portfolio = PortfolioManager()
journal = TradeJournal()

# Mount frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ─── Background state ────────────────────────────────────────────────────
_top25_cache: list = []
_global_news_cache: list = []


# ─── Routes ───────────────────────────────────────────────────────────────
@app.get("/")
async def serve_frontend():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "ANTIGRAVITY v3.0 API", "docs": "/docs"})


@app.get("/api/stock/{ticker}")
async def analyze_stock(ticker: str):
    """Full multi-agent analysis for a single ticker."""
    result = brain.full_analysis(ticker.upper())
    signal = generate_signal(result)
    result["signal"] = signal
    return result


@app.get("/api/quick/{ticker}")
async def quick_scan(ticker: str):
    """Quick technical scan — lightweight, for batch use."""
    return brain.quick_scan(ticker.upper())


@app.get("/api/price/{ticker}")
async def get_price(ticker: str):
    """Real-time price data."""
    return get_current_price(ticker.upper())


@app.get("/api/info/{ticker}")
async def get_info(ticker: str):
    """Extended ticker information."""
    return get_ticker_info(ticker.upper())


@app.get("/api/top25")
async def get_top25():
    """Live Top 25 ranked assets."""
    if _top25_cache:
        return {"top25": _top25_cache, "last_update": now_iso()}
    # Generate on-demand if cache empty
    results = []
    for t in TOP_25_WATCHLIST[:15]:
        try:
            scan = brain.quick_scan(t)
            price = get_current_price(t)
            results.append({**scan, **price})
        except Exception:
            continue
    sorted_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
    return {"top25": sorted_results[:25], "last_update": now_iso()}


@app.get("/api/top100")
async def get_top100():
    """All assets by category."""
    categories = {}
    for cat, tickers in ASSET_CATEGORIES.items():
        category_data = []
        for t in tickers[:25]:
            try:
                price = get_current_price(t)
                if "error" not in price:
                    name = COMMODITY_NAMES.get(t, t)
                    price["name"] = name
                    category_data.append(price)
            except Exception:
                continue
        categories[cat] = sorted(category_data, key=lambda x: abs(x.get("change_pct", 0)), reverse=True)
    return {"categories": categories, "timestamp": now_iso()}


@app.get("/api/news/{ticker}")
async def get_ticker_news(ticker: str):
    """News + sentiment for a specific ticker."""
    news = get_all_news(ticker.upper())
    sentiment = analyze_news_for_ticker(news)
    return {"ticker": ticker.upper(), "news": news, "sentiment": sentiment}


@app.get("/api/global-news")
async def get_global_news():
    """Global financial news feed."""
    if _global_news_cache:
        return {"news": _global_news_cache, "count": len(_global_news_cache)}
    news = get_all_news()
    sentiment = analyze_news_for_ticker(news)
    return {"news": news, "sentiment": sentiment, "count": len(news)}


@app.get("/api/predict/{ticker}")
async def predict_ticker(ticker: str):
    """AI prediction for a ticker."""
    return predictor.predict(ticker.upper())


@app.get("/api/signals")
async def get_signals():
    """Active trade signals."""
    return {"signals": get_active_signals(), "count": len(get_active_signals())}


@app.get("/api/portfolio")
async def get_portfolio():
    """Portfolio state + P&L."""
    return portfolio.get_portfolio_state()


@app.get("/api/performance")
async def get_performance():
    """Strategy performance metrics."""
    return journal.get_performance()


@app.get("/api/platforms")
async def get_platforms():
    """Top broker comparison."""
    return {"platforms": PLATFORMS, "count": len(PLATFORMS)}


@app.get("/api/report/{ticker}")
async def get_report(ticker: str):
    """Comprehensive AI report combining all data."""
    analysis = brain.full_analysis(ticker.upper())
    prediction = predictor.predict(ticker.upper())
    news = get_all_news(ticker.upper())
    sentiment = analyze_news_for_ticker(news)
    info = get_ticker_info(ticker.upper())

    return {
        "ticker": ticker.upper(),
        "info": info,
        "analysis": analysis,
        "prediction": prediction,
        "news": news[:10],
        "sentiment": sentiment,
        "generated_at": now_iso(),
    }


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "3.0.0", "timestamp": now_iso()}


# ─── AUTOBOT ENDPOINTS ────────────────────────────────────────────────────
@app.get("/api/bot/dashboard")
async def bot_dashboard():
    """Fetch Top 100 Platforms and general bot stats."""
    return {"platforms": PLATFORMS[:100], "status": "Autobot standby"}

@app.post("/api/bot/etoro/connect")
async def bot_etoro_connect():
    """Connect to eToro Mock."""
    return etoro_broker.connect()

@app.post("/api/bot/execute")
async def bot_execute():
    """Evaluate conditions and execute trade on eToro."""
    agent = BotAgent()
    eval_result = agent.evaluate_market_conditions()
    
    # Send order to eToro
    trade_result = etoro_broker.place_trade(
        ticker=eval_result["candidate"],
        action=eval_result["decision"]["action"],
        amount=eval_result["decision"]["amount"],
        take_profit=eval_result["decision"]["take_profit_multiplier"],
        stop_loss=eval_result["decision"]["stop_loss_multiplier"]
    )
    
    return {
        "evaluation": eval_result,
        "execution": trade_result
    }

# ─── Background scanner ──────────────────────────────────────────────────
def _background_scanner():
    """Background thread that refreshes Top 25 data."""
    global _top25_cache, _global_news_cache
    while True:
        try:
            log.info("Background scan: Top 25...")
            results = []
            for t in TOP_25_WATCHLIST[:15]:
                try:
                    scan = brain.quick_scan(t)
                    price = get_current_price(t)
                    results.append({**scan, **price})
                except Exception:
                    continue
            _top25_cache = sorted(results, key=lambda x: x.get("score", 0), reverse=True)

            log.info("Background scan: Global news...")
            _global_news_cache = get_all_news()

            log.info(f"Background scan complete: {len(_top25_cache)} assets, {len(_global_news_cache)} news")
        except Exception as e:
            log.error(f"Background scanner error: {e}")

        time.sleep(TOP25_SCAN_INTERVAL)


# Start background scanner
_scanner_thread = threading.Thread(target=_background_scanner, daemon=True)
_scanner_thread.start()

log.info("ANTIGRAVITY v3.0 — Server initialized")
