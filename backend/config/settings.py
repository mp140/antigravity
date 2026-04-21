"""
ANTIGRAVITY v3.0 — Configuration Loader
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from config dir if it exists
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# ─── API Keys (all optional — system works with Yahoo Finance alone) ─────
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
POLYGON_KEY = os.getenv("POLYGON_KEY", "")

# ─── Server Settings ─────────────────────────────────────────────────────
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# ─── Trading Parameters ──────────────────────────────────────────────────
STARTING_CAPITAL = float(os.getenv("STARTING_CAPITAL", "10000"))
MAX_RISK_PER_TRADE_PCT = 2.0
MAX_DAILY_LOSS_PCT = 5.0
MIN_CONFIDENCE_THRESHOLD = 75
MAX_OPEN_POSITIONS = 5
KELLY_FRACTION = 0.5
CIRCUIT_BREAKER_VIX = 35.0

# ─── Scanner Intervals (seconds) ─────────────────────────────────────────
TOP25_SCAN_INTERVAL = 60
NEWS_REFRESH_INTERVAL = 120
POSITION_MONITOR_INTERVAL = 30

# ─── Decision Engine Weights ─────────────────────────────────────────────
WEIGHT_TECHNICAL = 0.35
WEIGHT_AI_PREDICTION = 0.30
WEIGHT_SENTIMENT = 0.20
WEIGHT_PATTERN = 0.15
