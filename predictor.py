"""Predictor - simple time-series anomaly detection."""

import logging
import statistics
from collections import deque
from typing import Any, Deque, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


class Predictor:
    """Lightweight anomaly predictor using rolling statistics."""

    def __init__(self, window_size: int = 20, z_score_threshold: float = 2.5) -> None:
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self._series: Dict[str, Deque[float]] = {}
        self._predictions: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def record(self, metric: str, value: float) -> None:
        """Add a new observation for *metric*."""
        if metric not in self._series:
            self._series[metric] = deque(maxlen=self.window_size)
        self._series[metric].append(value)

    # ------------------------------------------------------------------
    # Anomaly detection
    # ------------------------------------------------------------------

    def is_anomaly(self, metric: str, value: float) -> Tuple[bool, Optional[float]]:
        """Return (is_anomaly, z_score) for the given value."""
        series = list(self._series.get(metric, []))
        if len(series) < 3:
            return False, None
        try:
            mean = statistics.mean(series)
            std = statistics.stdev(series)
        except statistics.StatisticsError:
            return False, None

        if std == 0:
            return False, 0.0

        z_score = abs(value - mean) / std
        return z_score > self.z_score_threshold, round(z_score, 3)

    def predict_next(self, metric: str) -> Optional[float]:
        """Naïve linear extrapolation of the next value."""
        series = list(self._series.get(metric, []))
        if len(series) < 2:
            return None
        # simple linear regression slope
        n = len(series)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(series)
        numerator = sum((i - x_mean) * (series[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        if denominator == 0:
            return y_mean
        slope = numerator / denominator
        return round(y_mean + slope, 4)

    def check_and_alert(self, metric: str, value: float) -> Optional[Dict[str, Any]]:
        """Record a value and return an alert dict if it is anomalous."""
        self.record(metric, value)
        anomaly, z_score = self.is_anomaly(metric, value)
        if not anomaly:
            return None
        alert = {
            "metric": metric,
            "value": value,
            "z_score": z_score,
            "prediction": self.predict_next(metric),
            "severity": "high" if z_score and z_score > self.z_score_threshold * 1.5 else "medium",
        }
        self._predictions.append(alert)
        logger.warning("Anomaly detected in '%s': value=%.3f z=%.3f", metric, value, z_score or 0)
        return alert

    def get_predictions(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._predictions[-limit:]

    def get_series_stats(self, metric: str) -> Dict[str, Any]:
        series = list(self._series.get(metric, []))
        if not series:
            return {"metric": metric, "count": 0}
        return {
            "metric": metric,
            "count": len(series),
            "mean": round(statistics.mean(series), 4),
            "stdev": round(statistics.stdev(series), 4) if len(series) > 1 else 0.0,
            "min": min(series),
            "max": max(series),
        }
