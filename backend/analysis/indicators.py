"""
ANTIGRAVITY v3.0 — Technical Indicators Engine
15+ indicators with multi-timeframe confluence scoring.
"""
import pandas as pd
import numpy as np
from typing import Optional
from backend.utils import get_logger

log = get_logger("Indicators")


def compute_all_indicators(df: pd.DataFrame) -> dict:
    """Compute full indicator suite on OHLCV DataFrame."""
    if df is None or len(df) < 30:
        return {"error": "Insufficient data", "signals": []}

    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values
    volume = df["Volume"].values if "Volume" in df.columns else np.zeros(len(close))

    # ─── RSI (14) ─────────────────────────────────────────────────────
    rsi_val = _rsi(close, 14)

    # ─── MACD ─────────────────────────────────────────────────────────
    macd_line, signal_line, histogram = _macd(close)

    # ─── EMAs ─────────────────────────────────────────────────────────
    ema9 = _ema(close, 9)
    ema21 = _ema(close, 21)
    ema50 = _ema(close, 50)
    ema200 = _ema(close, 200) if len(close) >= 200 else None

    # ─── Bollinger Bands ──────────────────────────────────────────────
    bb_upper, bb_middle, bb_lower = _bollinger(close, 20, 2)

    # ─── ATR (14) ─────────────────────────────────────────────────────
    atr = _atr(high, low, close, 14)

    # ─── Volume Analysis ──────────────────────────────────────────────
    vol_avg = float(np.mean(volume[-20:])) if len(volume) >= 20 else float(np.mean(volume))
    vol_current = float(volume[-1])
    vol_spike = vol_current > vol_avg * 1.5

    # ─── Support / Resistance ─────────────────────────────────────────
    support, resistance = _support_resistance(high, low, close)

    # ─── Generate Signals ─────────────────────────────────────────────
    signals = []
    current_price = float(close[-1])

    # RSI signals
    if rsi_val < 30:
        signals.append({"indicator": "RSI", "signal": "oversold", "value": round(rsi_val, 1), "bias": "bullish"})
    elif rsi_val > 70:
        signals.append({"indicator": "RSI", "signal": "overbought", "value": round(rsi_val, 1), "bias": "bearish"})

    # MACD signals
    if macd_line > signal_line and histogram > 0:
        signals.append({"indicator": "MACD", "signal": "bullish_crossover", "bias": "bullish"})
    elif macd_line < signal_line and histogram < 0:
        signals.append({"indicator": "MACD", "signal": "bearish_crossover", "bias": "bearish"})

    # EMA signals
    if ema9 > ema21:
        signals.append({"indicator": "EMA", "signal": "short_term_bullish", "bias": "bullish"})
    if ema200 is not None:
        if current_price > ema200:
            signals.append({"indicator": "EMA200", "signal": "above_200ema", "bias": "bullish"})
        else:
            signals.append({"indicator": "EMA200", "signal": "below_200ema", "bias": "bearish"})

    # Bollinger Band signals
    if current_price < bb_lower:
        signals.append({"indicator": "Bollinger", "signal": "below_lower_band", "bias": "bullish"})
    elif current_price > bb_upper:
        signals.append({"indicator": "Bollinger", "signal": "above_upper_band", "bias": "bearish"})

    # Volume spike
    if vol_spike:
        signals.append({"indicator": "Volume", "signal": "volume_spike", "value": round(vol_current / vol_avg, 1), "bias": "neutral"})

    # ─── Trend Determination ──────────────────────────────────────────
    bullish_count = sum(1 for s in signals if s["bias"] == "bullish")
    bearish_count = sum(1 for s in signals if s["bias"] == "bearish")

    if bullish_count > bearish_count + 1:
        trend = "bullish"
    elif bearish_count > bullish_count + 1:
        trend = "bearish"
    else:
        trend = "neutral"

    # Strength score (0-100)
    total = bullish_count + bearish_count
    strength = int((bullish_count / max(total, 1)) * 100) if trend == "bullish" else int((1 - bearish_count / max(total, 1)) * 100) if trend == "bearish" else 50

    return {
        "trend": trend,
        "strength_score": strength,
        "signals": signals,
        "indicators": {
            "rsi": round(rsi_val, 2),
            "macd": round(macd_line, 4),
            "macd_signal": round(signal_line, 4),
            "macd_histogram": round(histogram, 4),
            "ema9": round(ema9, 4),
            "ema21": round(ema21, 4),
            "ema50": round(ema50, 4),
            "ema200": round(ema200, 4) if ema200 else None,
            "bb_upper": round(bb_upper, 4),
            "bb_middle": round(bb_middle, 4),
            "bb_lower": round(bb_lower, 4),
            "atr": round(atr, 4),
        },
        "volume": {
            "current": int(vol_current),
            "average": int(vol_avg),
            "spike": vol_spike,
            "ratio": round(vol_current / max(vol_avg, 1), 2),
        },
        "support": round(support, 4),
        "resistance": round(resistance, 4),
        "current_price": round(current_price, 4),
    }


# ─── Indicator implementations ───────────────────────────────────────────
def _rsi(close: np.ndarray, period: int = 14) -> float:
    deltas = np.diff(close)
    gain = np.where(deltas > 0, deltas, 0)
    loss = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _ema(data: np.ndarray, period: int) -> float:
    if len(data) < period:
        return float(np.mean(data))
    multiplier = 2 / (period + 1)
    ema = float(np.mean(data[:period]))
    for price in data[period:]:
        ema = (float(price) - ema) * multiplier + ema
    return ema


def _macd(close: np.ndarray, fast: int = 12, slow: int = 26, signal_period: int = 9):
    ema_fast = _compute_ema_series(close, fast)
    ema_slow = _compute_ema_series(close, slow)
    macd_line_series = ema_fast - ema_slow
    signal = _compute_ema_series(macd_line_series, signal_period)
    hist = macd_line_series - signal
    return float(macd_line_series[-1]), float(signal[-1]), float(hist[-1])


def _compute_ema_series(data: np.ndarray, period: int) -> np.ndarray:
    result = np.zeros_like(data, dtype=float)
    result[0] = float(data[0])
    multiplier = 2 / (period + 1)
    for i in range(1, len(data)):
        result[i] = (float(data[i]) - result[i - 1]) * multiplier + result[i - 1]
    return result


def _bollinger(close: np.ndarray, period: int = 20, std_dev: int = 2):
    sma = float(np.mean(close[-period:]))
    std = float(np.std(close[-period:]))
    return sma + std_dev * std, sma, sma - std_dev * std


def _atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> float:
    tr = np.maximum(high[1:] - low[1:], np.maximum(abs(high[1:] - close[:-1]), abs(low[1:] - close[:-1])))
    return float(np.mean(tr[-period:]))


def _support_resistance(high: np.ndarray, low: np.ndarray, close: np.ndarray):
    recent_low = float(np.min(low[-20:]))
    recent_high = float(np.max(high[-20:]))
    return recent_low, recent_high
