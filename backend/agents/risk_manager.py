"""
ANTIGRAVITY v3.0 — CRO Risk Manager Agent
Position sizing (Kelly Criterion), stop-loss, circuit breakers.
"""
import numpy as np
from backend.data.market_fetcher import get_stock_data, get_current_price
from backend.analysis.indicators import _atr
from backend.config.settings import (
    STARTING_CAPITAL, MAX_RISK_PER_TRADE_PCT, MAX_OPEN_POSITIONS,
    KELLY_FRACTION, CIRCUIT_BREAKER_VIX, MAX_DAILY_LOSS_PCT,
)
from backend.utils import get_logger

log = get_logger("Agent:RiskMgr")


class RiskManagerAgent:
    """Chief Risk Officer — position sizing, stop-loss, circuit breakers."""

    def __init__(self):
        self.capital = STARTING_CAPITAL
        self.daily_pnl = 0.0

    def analyze(self, ticker: str, confidence: float, direction: str = "long") -> dict:
        """Compute risk parameters for a potential trade."""
        log.info(f"Risk assessment: {ticker} (conf={confidence:.0f}%)")

        price_data = get_current_price(ticker)
        current_price = price_data.get("price", 0)
        if current_price == 0:
            return {"ticker": ticker, "approved": False, "reason": "No price data"}

        # Check circuit breakers
        breaker = self._check_circuit_breakers()
        if breaker:
            return {"ticker": ticker, "approved": False, "reason": breaker}

        # ATR-based stop loss
        df = get_stock_data(ticker, period="1mo", interval="1d")
        if df is not None and len(df) >= 15:
            atr = _atr(df["High"].values, df["Low"].values, df["Close"].values, 14)
        else:
            atr = current_price * 0.02  # fallback 2%

        stop_loss_distance = atr * 1.5
        stop_loss = current_price - stop_loss_distance if direction == "long" else current_price + stop_loss_distance

        # Kelly Criterion position sizing
        win_rate = min(confidence / 100, 0.9)
        avg_win_loss_ratio = 2.0  # assume 2:1 R:R
        kelly_pct = (win_rate * avg_win_loss_ratio - (1 - win_rate)) / avg_win_loss_ratio
        kelly_pct = max(0, kelly_pct * KELLY_FRACTION)

        # Risk-based position size
        risk_amount = self.capital * (MAX_RISK_PER_TRADE_PCT / 100)
        shares_by_risk = int(risk_amount / max(stop_loss_distance, 0.01))
        shares_by_kelly = int((self.capital * kelly_pct) / max(current_price, 0.01))
        position_size = min(shares_by_risk, shares_by_kelly, int(self.capital * 0.2 / max(current_price, 0.01)))
        position_size = max(1, position_size)

        # Take profit levels
        tp1 = current_price + stop_loss_distance * 2 if direction == "long" else current_price - stop_loss_distance * 2
        tp2 = current_price + stop_loss_distance * 3 if direction == "long" else current_price - stop_loss_distance * 3

        risk_reward = round(stop_loss_distance * 2 / max(stop_loss_distance, 0.001), 1)

        approved = confidence >= 70 and kelly_pct > 0 and position_size > 0

        result = {
            "ticker": ticker,
            "approved": approved,
            "direction": direction,
            "entry_price": round(current_price, 4),
            "stop_loss": round(stop_loss, 4),
            "take_profit_1": round(tp1, 4),
            "take_profit_2": round(tp2, 4),
            "position_size": position_size,
            "position_value": round(position_size * current_price, 2),
            "risk_amount": round(position_size * stop_loss_distance, 2),
            "risk_reward_ratio": f"1:{risk_reward}",
            "kelly_pct": round(kelly_pct * 100, 2),
            "atr": round(atr, 4),
        }
        log.info(f"{ticker}: {'APPROVED' if approved else 'REJECTED'} | Size={position_size} SL={stop_loss:.2f}")
        return result

    def _check_circuit_breakers(self) -> str:
        """Check if any circuit breakers are triggered."""
        # VIX check
        try:
            vix = get_current_price("^VIX")
            if isinstance(vix, dict) and vix.get("price", 0) > CIRCUIT_BREAKER_VIX:
                return f"VIX above {CIRCUIT_BREAKER_VIX} — circuit breaker active"
        except Exception:
            pass

        # Daily loss check
        if abs(self.daily_pnl) > self.capital * (MAX_DAILY_LOSS_PCT / 100):
            return f"Daily loss limit ({MAX_DAILY_LOSS_PCT}%) reached"

        return ""
