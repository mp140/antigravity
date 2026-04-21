"""
ANTIGRAVITY v3.0 — Shared Utilities
"""
import datetime as _dt
import logging
import json
import os

# ─── Logging ──────────────────────────────────────────────────────────────
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("[%(asctime)s] %(name)-20s  %(levelname)-7s  %(message)s", datefmt="%H:%M:%S")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


# ─── JSON helpers ─────────────────────────────────────────────────────────
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)


def load_json(filename: str, default=None):
    path = os.path.join(MEMORY_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default if default is not None else {}


def save_json(filename: str, data):
    path = os.path.join(MEMORY_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ─── Formatting helpers ──────────────────────────────────────────────────
def fmt_pct(val: float) -> str:
    if val is None:
        return "N/A"
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.2f}%"


def fmt_price(val: float) -> str:
    if val is None:
        return "N/A"
    if abs(val) >= 1:
        return f"${val:,.2f}"
    return f"${val:.6f}"


def fmt_volume(val: float) -> str:
    if val is None:
        return "N/A"
    if val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.2f}B"
    if val >= 1_000_000:
        return f"{val / 1_000_000:.2f}M"
    if val >= 1_000:
        return f"{val / 1_000:.1f}K"
    return str(int(val))


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def safe_get(d: dict, *keys, default=None):
    """Safely navigate nested dicts."""
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
        else:
            return default
    return d
