"""
ANTIGRAVITY v3.0 — AI Predictor
Sklearn ensemble (RandomForest + GradientBoosting) for price direction prediction.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from backend.data.market_fetcher import get_stock_data
from backend.analysis.indicators import _rsi, _ema, _macd
from backend.utils import get_logger

log = get_logger("AI:Predictor")


class AIPredictor:
    """Ensemble ML predictor for price direction."""

    def __init__(self):
        self.models = {}

    def predict(self, ticker: str) -> dict:
        """Predict next-day price direction for a ticker."""
        log.info(f"AI prediction: {ticker}")
        df = get_stock_data(ticker, period="1y", interval="1d")
        if df is None or len(df) < 60:
            return {"ticker": ticker, "error": "Insufficient data", "probability_up": 0.5, "confidence": 0}

        try:
            features, labels = self._prepare_features(df)
            if len(features) < 30:
                return {"ticker": ticker, "error": "Not enough features", "probability_up": 0.5, "confidence": 0}

            # Train/test split
            split = int(len(features) * 0.8)
            X_train, X_test = features[:split], features[split:]
            y_train, y_test = labels[:split], labels[split:]

            # Ensemble
            rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
            gb = GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=3)

            rf.fit(X_train, y_train)
            gb.fit(X_train, y_train)

            # Predict on latest features
            latest = features[-1:].copy()
            rf_prob = rf.predict_proba(latest)[0]
            gb_prob = gb.predict_proba(latest)[0]

            # Ensemble average
            prob_up = (rf_prob[1] + gb_prob[1]) / 2 if len(rf_prob) > 1 else 0.5

            # Test accuracy
            rf_acc = float(rf.score(X_test, y_test))
            gb_acc = float(gb.score(X_test, y_test))
            avg_acc = (rf_acc + gb_acc) / 2

            # Confidence based on prediction strength and model accuracy
            confidence = round(abs(prob_up - 0.5) * 2 * avg_acc * 100, 1)

            current_price = float(df["Close"].iloc[-1])
            predicted_move = (prob_up - 0.5) * 4  # rough percentage estimate

            result = {
                "ticker": ticker,
                "probability_up": round(prob_up, 4),
                "probability_down": round(1 - prob_up, 4),
                "confidence": min(confidence, 95),
                "predicted_move_pct": round(predicted_move, 2),
                "direction": "UP" if prob_up > 0.55 else "DOWN" if prob_up < 0.45 else "SIDEWAYS",
                "model_accuracy": {
                    "random_forest": round(rf_acc * 100, 1),
                    "gradient_boosting": round(gb_acc * 100, 1),
                    "ensemble": round(avg_acc * 100, 1),
                },
                "current_price": round(current_price, 4),
                "timeframe": "next_day",
            }
            log.info(f"{ticker}: P(up)={prob_up:.3f} Conf={confidence:.0f}% Dir={result['direction']}")
            return result

        except Exception as e:
            log.error(f"Prediction failed for {ticker}: {e}")
            return {"ticker": ticker, "error": str(e), "probability_up": 0.5, "confidence": 0}

    def _prepare_features(self, df: pd.DataFrame) -> tuple:
        """Create ML features from OHLCV data."""
        close = df["Close"].values
        high = df["High"].values
        low = df["Low"].values
        volume = df["Volume"].values if "Volume" in df.columns else np.zeros(len(close))

        features = []
        labels = []
        lookback = 20

        for i in range(lookback, len(close) - 1):
            window = close[i - lookback:i]
            vol_window = volume[i - lookback:i]

            rsi = _rsi(window, 14)
            ema_fast = _ema(window, 9)
            ema_slow = _ema(window, 21)
            price_change_5d = (close[i] - close[i - 5]) / close[i - 5] * 100
            price_change_10d = (close[i] - close[i - 10]) / close[i - 10] * 100
            volatility = float(np.std(window[-10:])) / float(np.mean(window[-10:])) * 100
            vol_ratio = float(volume[i]) / max(float(np.mean(vol_window)), 1)
            high_low_pct = (float(high[i]) - float(low[i])) / float(close[i]) * 100
            dist_from_high = (float(np.max(window)) - float(close[i])) / float(np.max(window)) * 100
            day_of_week = i % 5

            features.append([
                rsi, ema_fast - ema_slow, price_change_5d, price_change_10d,
                volatility, vol_ratio, high_low_pct, dist_from_high, day_of_week,
            ])

            # Label: 1 if next day close is higher
            labels.append(1 if close[i + 1] > close[i] else 0)

        return np.array(features), np.array(labels)
