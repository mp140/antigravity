"""
ANTIGRAVITY v3.0 — Trade Journal
Records all trades with full metadata and performance analytics.
"""
from backend.utils import load_json, save_json, now_iso, get_logger

log = get_logger("TradeJournal")


class TradeJournal:
    """Records and analyzes all trading activity."""

    def __init__(self):
        self.entries = load_json("trade_journal.json", [])

    def record_trade(self, trade: dict):
        """Record a completed trade."""
        entry = {
            "ticker": trade.get("ticker"),
            "direction": trade.get("direction"),
            "entry_price": trade.get("entry_price"),
            "exit_price": trade.get("exit_price"),
            "quantity": trade.get("quantity"),
            "pnl": trade.get("pnl", 0),
            "reason": trade.get("reason", ""),
            "opened_at": trade.get("opened_at"),
            "closed_at": trade.get("closed_at", now_iso()),
        }
        self.entries.append(entry)
        save_json("trade_journal.json", self.entries)
        log.info(f"Recorded: {entry['ticker']} PnL=${entry['pnl']:.2f}")

    def get_performance(self) -> dict:
        """Get aggregated performance metrics."""
        if not self.entries:
            return {"total_trades": 0, "message": "No trades recorded yet"}

        pnls = [e.get("pnl", 0) for e in self.entries]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]

        return {
            "total_trades": len(self.entries),
            "total_pnl": round(sum(pnls), 2),
            "win_rate": round(len(wins) / len(pnls) * 100, 1),
            "avg_win": round(sum(wins) / max(len(wins), 1), 2),
            "avg_loss": round(sum(losses) / max(len(losses), 1), 2),
            "best_trade": round(max(pnls), 2) if pnls else 0,
            "worst_trade": round(min(pnls), 2) if pnls else 0,
            "profit_factor": round(sum(wins) / max(abs(sum(losses)), 0.01), 2) if losses else 999,
            "recent_trades": self.entries[-10:],
        }
