"""
ANTIGRAVITY v3.0 — Asset Universe & Platform Constants
"""

# ─── STOCK UNIVERSE (Top traded US stocks) ────────────────────────────────
STOCKS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "BRK-B",
    "LLY", "AVGO", "JPM", "V", "UNH", "MA", "XOM", "JNJ", "PG", "HD",
    "COST", "ABBV", "MRK", "CRM", "AMD", "NFLX", "ADBE", "PEP", "TMO",
    "ORCL", "ACN", "CSCO", "MCD", "INTC", "ABT", "CMCSA", "NKE", "WMT",
    "DIS", "QCOM", "TXN", "PM", "INTU", "LOW", "IBM", "GE", "CAT",
    "BA", "UBER", "AMAT", "PLTR", "COIN",
]

# ─── CRYPTO UNIVERSE ──────────────────────────────────────────────────────
CRYPTO = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
    "ADA-USD", "DOGE-USD", "AVAX-USD", "DOT-USD", "MATIC-USD",
]

# ─── FOREX PAIRS ──────────────────────────────────────────────────────────
FOREX = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X",
    "USDCAD=X", "USDCHF=X", "NZDUSD=X", "EURGBP=X",
]

# ─── COMMODITIES ──────────────────────────────────────────────────────────
COMMODITIES = [
    "GC=F",   # Gold
    "SI=F",   # Silver
    "CL=F",   # Crude Oil
    "NG=F",   # Natural Gas
    "HG=F",   # Copper
    "PL=F",   # Platinum
    "ZW=F",   # Wheat
    "ZC=F",   # Corn
    "KC=F",   # Coffee
    "CT=F",   # Cotton
]

# ─── KEY ETFs ─────────────────────────────────────────────────────────────
ETFS = [
    "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "ARKK", "XLF",
    "XLE", "XLK", "XLV", "SCHD", "VGT", "SOXX", "SMH", "TLT",
    "GLD", "SLV", "USO", "IBIT", "TQQQ", "SQQQ", "VIX",
]

# ─── ASSET CATEGORY MAP ──────────────────────────────────────────────────
ASSET_CATEGORIES = {
    "stocks": STOCKS,
    "crypto": CRYPTO,
    "forex": FOREX,
    "commodities": COMMODITIES,
    "etfs": ETFS,
}

ALL_TICKERS = STOCKS + CRYPTO + FOREX + COMMODITIES + ETFS

# ─── TOP 25 SCANNER WATCHLIST (most actively traded) ─────────────────────
TOP_25_WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA",
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD",
    "SPY", "QQQ", "GC=F", "CL=F",
    "AMD", "NFLX", "PLTR", "COIN", "UBER",
    "AVGO", "CRM", "ADBE", "JPM", "BA",
]

# ─── COMMODITY LABELS ────────────────────────────────────────────────────
COMMODITY_NAMES = {
    "GC=F": "Gold", "SI=F": "Silver", "CL=F": "Crude Oil",
    "NG=F": "Natural Gas", "HG=F": "Copper", "PL=F": "Platinum",
    "ZW=F": "Wheat", "ZC=F": "Corn", "KC=F": "Coffee", "CT=F": "Cotton",
}

# ─── PLATFORM DATABASE ───────────────────────────────────────────────────
PLATFORMS = [
    {"rank": 1, "name": "QuantConnect", "type": "Open Source", "reliability": "⭐⭐⭐⭐⭐", "evidence": "Strong (Institutional)", "verdict": "BEST CODE-FIRST SYSTEM", "rating": 4.9, "api": True},
    {"rank": 2, "name": "MetaTrader 5", "type": "Multi-Asset", "reliability": "⭐⭐⭐⭐⭐", "evidence": "Proven (Global)", "verdict": "BEST FOR FOREX & SCALPING", "rating": 4.8, "api": True},
    {"rank": 3, "name": "Trade Ideas", "type": "AI Signals", "reliability": "⭐⭐⭐⭐", "evidence": "Verified Signals", "verdict": "BEST AI MARKET SCANNER", "rating": 4.7, "api": True},
    {"rank": 4, "name": "3Commas", "type": "Crypto Bot", "reliability": "⭐⭐⭐", "evidence": "Mixed/Skill-based", "verdict": "BEST FOR CRYPTO DCA/GRID", "rating": 4.3, "api": True},
    {"rank": 5, "name": "Pionex", "type": "Exchange Bot", "reliability": "⭐⭐⭐", "evidence": "Consistent Low-Fee", "verdict": "BEST INTEGRATED EXCHANGE BOTS", "rating": 4.5, "api": True},
    {"rank": 6, "name": "Interactive Brokers", "type": "Deep API", "reliability": "⭐⭐⭐⭐⭐", "evidence": "Institutional", "verdict": "BEST FOR PRO CONNECTIVITY", "rating": 4.8, "api": True},
    {"rank": 7, "name": "HaasOnline", "type": "Crypto Scripting", "reliability": "⭐⭐⭐⭐", "evidence": "Professional", "verdict": "BEST FOR ADVANCED SCRIPTING", "rating": 4.6, "api": True},
    {"rank": 8, "name": "Cryptohopper", "type": "Cloud Bot", "reliability": "⭐⭐⭐", "evidence": "Moderate", "verdict": "BEST CLOUD-BASED SETUP", "rating": 4.4, "api": True},
    {"rank": 9, "name": "Alpaca", "type": "Stock API", "reliability": "⭐⭐⭐", "evidence": "Growth", "verdict": "BEST FOR DEVELOPER APIS", "rating": 4.4, "api": True},
    {"rank": 10, "name": "Composer", "type": "No-Code Algo", "reliability": "⭐⭐⭐", "evidence": "Emerging", "verdict": "BEST FOR NO-CODE ETF ALGO", "rating": 4.2, "api": True},
    {"rank": 11, "name": "Gunbot", "type": "Privacy-First", "reliability": "⭐⭐⭐⭐", "evidence": "Local Privacy", "verdict": "BEST FOR SECURE LOCAL BOTS", "rating": 4.5, "api": True},
    {"rank": 12, "name": "NinjaTrader", "type": "Pro Trading", "reliability": "⭐⭐⭐⭐⭐", "evidence": "High", "verdict": "BEST DESKTOP BACKTESTING", "rating": 4.7, "api": True},
    {"rank": 13, "name": "TradeStation", "type": "Full Broker", "reliability": "⭐⭐⭐⭐⭐", "evidence": "Professional", "verdict": "BEST BUILT-IN SIGNAL ENGINE", "rating": 4.7, "api": True},
    {"rank": 14, "name": "Bitsgap", "type": "Multi-Ex", "reliability": "⭐⭐⭐", "evidence": "Moderate", "verdict": "BEST MULTI-EX ARBITRAGE", "rating": 4.3, "api": True},
    {"rank": 15, "name": "Shrimpy", "type": "Crypto Rebal", "reliability": "⭐⭐⭐", "evidence": "High (Rebal)", "verdict": "BEST FOR PORTFOLIO REBALANCING", "rating": 4.4, "api": True},
    {"rank": 16, "name": "Tickeron", "type": "AI Forecast", "reliability": "⭐⭐⭐", "evidence": "Verifiable AI", "verdict": "BEST FOR AI RECOGNITION", "rating": 4.1, "api": True},
    {"rank": 17, "name": "Scanz", "type": "L2 Scan", "reliability": "⭐⭐⭐⭐", "evidence": "Real-time", "verdict": "BEST FOR DAY TRADING SCANS", "rating": 4.5, "api": True},
    {"rank": 18, "name": "TrendSpider", "type": "Chart Auto", "reliability": "⭐⭐⭐⭐", "evidence": "Backtested", "verdict": "BEST CHART AUTOMATION", "rating": 4.6, "api": True},
    {"rank": 19, "name": "Kryll.io", "type": "Visual Builder", "reliability": "⭐⭐⭐", "evidence": "Community", "verdict": "BEST VISUAL DRAG-AND-DROP", "rating": 4.2, "api": True},
    {"rank": 20, "name": "Coinrule", "type": "Rule-Based", "reliability": "⭐⭐⭐", "evidence": "Simple", "verdict": "BEST FOR BEGINNER RULES", "rating": 4.1, "api": True},
]

