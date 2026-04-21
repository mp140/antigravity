"""
ANTIGRAVITY v3.0 — Strategy Learner
Self-improving weight optimization based on historical performance.
"""
from backend.utils import load_json, save_json, get_logger

log = get_logger("StrategyLearner")


class StrategyLearner:
    """Analyzes past trades and suggests weight adjustments."""

    def __init__(self):
        self.performance = load_json("strategy_performance.json", {
            "adjustments": [],
            "current_weights": {
                "technical": 0.35,
                "ai_prediction": 0.30,
                "sentiment": 0.20,
                "pattern": 0.15,
            }
        })

    def analyze_and_suggest(self) -> dict:
        """Analyze recent trade outcomes and suggest weight adjustments."""
        journal = load_json("trade_journal.json", [])
        if len(journal) < 5:
            return {"message": "Need at least 5 trades for analysis", "suggestions": []}

        recent = journal[-20:]
        wins = [t for t in recent if t.get("pnl", 0) > 0]
        losses = [t for t in recent if t.get("pnl", 0) <= 0]

        win_rate = len(wins) / len(recent) * 100
        suggestions = []

        if win_rate < 40:
            suggestions.append("Consider increasing technical weight — fundamentals may be underweighted")
        if win_rate > 70:
            suggestions.append("Strong performance — current weights are working well")

        return {
            "recent_win_rate": round(win_rate, 1),
            "sample_size": len(recent),
            "current_weights": self.performance["current_weights"],
            "suggestions": suggestions,
        }
