"""
ANTIGRAVITY v3.0 — Signal Generator
Produces actionable trade signals from Master Brain analysis.
"""
from backend.utils import get_logger, now_iso, save_json, load_json

log = get_logger("SignalGen")

_active_signals: list = []


def generate_signal(analysis: dict) -> dict:
    """Generate a trade signal from a full analysis result."""
    action = analysis.get("action", "HOLD")
    if action == "HOLD":
        return {"ticker": analysis.get("ticker"), "action": "HOLD", "reason": "No actionable signal"}

    risk = analysis.get("risk", {})
    if not risk.get("approved", False):
        return {"ticker": analysis.get("ticker"), "action": "HOLD", "reason": "Risk manager rejected"}

    signal = {
        "ticker": analysis["ticker"],
        "action": action,
        "direction": risk.get("direction", "long"),
        "entry_price": risk.get("entry_price"),
        "stop_loss": risk.get("stop_loss"),
        "take_profit_1": risk.get("take_profit_1"),
        "take_profit_2": risk.get("take_profit_2"),
        "position_size": risk.get("position_size"),
        "risk_reward": risk.get("risk_reward_ratio"),
        "confidence": analysis.get("confidence"),
        "final_score": analysis.get("final_score"),
        "generated_at": now_iso(),
        "macro_regime": analysis.get("macro", {}).get("regime"),
        "technical_trend": analysis.get("technical", {}).get("trend"),
        "sentiment_label": analysis.get("sentiment", {}).get("label"),
        "status": "active",
    }

    _active_signals.append(signal)
    # Keep only last 50 signals
    if len(_active_signals) > 50:
        _active_signals.pop(0)

    save_json("active_signals.json", _active_signals)
    log.info(f"Signal: {action} {analysis['ticker']} @ {risk.get('entry_price')} | SL={risk.get('stop_loss')} TP1={risk.get('take_profit_1')}")
    return signal


def get_active_signals() -> list:
    """Return all active trade signals."""
    return _active_signals


def clear_signals():
    """Clear all signals."""
    _active_signals.clear()
    save_json("active_signals.json", [])
