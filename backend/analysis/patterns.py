"""
ANTIGRAVITY v3.0 — Candlestick Pattern Recognition
Detects key candlestick patterns with volume confirmation.
"""
import numpy as np
import pandas as pd
from backend.utils import get_logger

log = get_logger("Patterns")


def detect_patterns(df: pd.DataFrame) -> dict:
    """Detect candlestick patterns on OHLCV data."""
    if df is None or len(df) < 5:
        return {"patterns": [], "summary": "Insufficient data"}

    o = df["Open"].values
    h = df["High"].values
    l = df["Low"].values
    c = df["Close"].values
    v = df["Volume"].values if "Volume" in df.columns else np.ones(len(c))

    patterns = []
    body = c - o
    upper_shadow = h - np.maximum(c, o)
    lower_shadow = np.minimum(c, o) - l
    body_size = np.abs(body)
    candle_range = h - l

    avg_body = float(np.mean(body_size[-20:])) if len(body_size) >= 20 else float(np.mean(body_size))
    avg_vol = float(np.mean(v[-20:])) if len(v) >= 20 else float(np.mean(v))

    # Check last 3 candles for patterns
    for i in range(-3, 0):
        idx = len(c) + i
        if idx < 2:
            continue

        bs = float(body_size[idx])
        cr = float(candle_range[idx]) if candle_range[idx] > 0 else 0.001
        us = float(upper_shadow[idx])
        ls = float(lower_shadow[idx])
        is_bullish = float(body[idx]) > 0
        vol_confirm = float(v[idx]) > avg_vol * 1.2

        # ── Hammer (bullish reversal) ──
        if ls > bs * 2 and us < bs * 0.5 and not is_bullish:
            patterns.append({
                "name": "Hammer",
                "type": "bullish_reversal",
                "candle_index": i,
                "confidence": 75 + (15 if vol_confirm else 0),
                "volume_confirmed": vol_confirm,
            })

        # ── Shooting Star (bearish reversal) ──
        if us > bs * 2 and ls < bs * 0.5 and is_bullish:
            patterns.append({
                "name": "Shooting Star",
                "type": "bearish_reversal",
                "candle_index": i,
                "confidence": 75 + (15 if vol_confirm else 0),
                "volume_confirmed": vol_confirm,
            })

        # ── Doji ──
        if bs < cr * 0.1:
            doji_type = "gravestone" if us > ls * 2 else "dragonfly" if ls > us * 2 else "standard"
            patterns.append({
                "name": f"Doji ({doji_type})",
                "type": "indecision",
                "candle_index": i,
                "confidence": 60,
                "volume_confirmed": vol_confirm,
            })

        # ── Engulfing ──
        if idx >= 1:
            prev_body = float(body[idx - 1])
            if is_bullish and prev_body < 0 and bs > abs(prev_body) * 1.2:
                patterns.append({
                    "name": "Bullish Engulfing",
                    "type": "bullish_reversal",
                    "candle_index": i,
                    "confidence": 80 + (10 if vol_confirm else 0),
                    "volume_confirmed": vol_confirm,
                })
            elif not is_bullish and prev_body > 0 and bs > abs(prev_body) * 1.2:
                patterns.append({
                    "name": "Bearish Engulfing",
                    "type": "bearish_reversal",
                    "candle_index": i,
                    "confidence": 80 + (10 if vol_confirm else 0),
                    "volume_confirmed": vol_confirm,
                })

        # ── Large body (momentum) ──
        if bs > avg_body * 2:
            direction = "bullish" if is_bullish else "bearish"
            patterns.append({
                "name": f"Strong {direction.title()} Candle",
                "type": f"{direction}_momentum",
                "candle_index": i,
                "confidence": 70 + (15 if vol_confirm else 0),
                "volume_confirmed": vol_confirm,
            })

    # ── Summary ──
    bullish_patterns = [p for p in patterns if "bullish" in p["type"]]
    bearish_patterns = [p for p in patterns if "bearish" in p["type"]]

    if len(bullish_patterns) > len(bearish_patterns):
        summary = "bullish"
    elif len(bearish_patterns) > len(bullish_patterns):
        summary = "bearish"
    else:
        summary = "neutral"

    avg_conf = float(np.mean([p["confidence"] for p in patterns])) if patterns else 50

    return {
        "patterns": patterns,
        "summary": summary,
        "pattern_count": len(patterns),
        "bullish_count": len(bullish_patterns),
        "bearish_count": len(bearish_patterns),
        "avg_confidence": round(avg_conf, 1),
    }
