"""
ANTIGRAVITY v3.0 — Portfolio Manager
Position tracking, P&L calculation, auto-close logic.
"""
from backend.utils import get_logger, save_json, load_json, now_iso
from backend.data.market_fetcher import get_current_price
from backend.config.settings import STARTING_CAPITAL

log = get_logger("Portfolio")


class PortfolioManager:
    """Track open positions and P&L."""

    def __init__(self):
        self.capital = STARTING_CAPITAL
        self.positions = load_json("positions.json", [])
        self.closed_trades = load_json("closed_trades.json", [])

    def open_position(self, signal: dict) -> dict:
        """Open a new position from a trade signal."""
        position = {
            "ticker": signal["ticker"],
            "direction": signal.get("direction", "long"),
            "entry_price": signal["entry_price"],
            "stop_loss": signal["stop_loss"],
            "take_profit_1": signal["take_profit_1"],
            "take_profit_2": signal.get("take_profit_2"),
            "quantity": signal.get("position_size", 1),
            "opened_at": now_iso(),
            "status": "open",
        }
        self.positions.append(position)
        self._save()
        log.info(f"Opened: {position['direction'].upper()} {position['ticker']} x{position['quantity']} @ {position['entry_price']}")
        return position

    def close_position(self, ticker: str, reason: str = "manual") -> dict:
        """Close a position by ticker."""
        for i, pos in enumerate(self.positions):
            if pos["ticker"] == ticker and pos["status"] == "open":
                current = get_current_price(ticker)
                exit_price = current.get("price", pos["entry_price"])
                pnl = (exit_price - pos["entry_price"]) * pos["quantity"]
                if pos["direction"] == "short":
                    pnl = -pnl

                closed = {**pos, "exit_price": exit_price, "pnl": round(pnl, 2), "closed_at": now_iso(), "reason": reason, "status": "closed"}
                self.closed_trades.append(closed)
                self.positions.pop(i)
                self.capital += pnl
                self._save()
                log.info(f"Closed: {ticker} PnL=${pnl:.2f} ({reason})")
                return closed
        return {"error": f"No open position for {ticker}"}

    def get_portfolio_state(self) -> dict:
        """Get full portfolio state with unrealized P&L."""
        open_positions = []
        total_unrealized = 0

        for pos in self.positions:
            if pos["status"] != "open":
                continue
            current = get_current_price(pos["ticker"])
            price = current.get("price", pos["entry_price"])
            unrealized = (price - pos["entry_price"]) * pos["quantity"]
            if pos["direction"] == "short":
                unrealized = -unrealized

            open_positions.append({
                **pos,
                "current_price": price,
                "unrealized_pnl": round(unrealized, 2),
                "pnl_pct": round(unrealized / (pos["entry_price"] * pos["quantity"]) * 100, 2),
            })
            total_unrealized += unrealized

        total_realized = sum(t.get("pnl", 0) for t in self.closed_trades)
        win_trades = [t for t in self.closed_trades if t.get("pnl", 0) > 0]
        loss_trades = [t for t in self.closed_trades if t.get("pnl", 0) <= 0]

        return {
            "capital": round(self.capital, 2),
            "starting_capital": STARTING_CAPITAL,
            "total_return": round((self.capital - STARTING_CAPITAL) / STARTING_CAPITAL * 100, 2),
            "open_positions": open_positions,
            "open_count": len(open_positions),
            "total_unrealized_pnl": round(total_unrealized, 2),
            "total_realized_pnl": round(total_realized, 2),
            "total_trades": len(self.closed_trades),
            "win_rate": round(len(win_trades) / max(len(self.closed_trades), 1) * 100, 1),
            "avg_win": round(sum(t["pnl"] for t in win_trades) / max(len(win_trades), 1), 2),
            "avg_loss": round(sum(t["pnl"] for t in loss_trades) / max(len(loss_trades), 1), 2),
        }

    def _save(self):
        save_json("positions.json", self.positions)
        save_json("closed_trades.json", self.closed_trades)
