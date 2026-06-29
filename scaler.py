"""Auto-scaler - adjusts Docker service replicas based on load."""
import logging, subprocess
from datetime import datetime
from typing import Any, Dict, List
logger = logging.getLogger(__name__)

class AutoScaler:
    def __init__(self, compose_file="docker/docker-compose.yml",
                 min_replicas=1, max_replicas=10,
                 scale_up_cpu_threshold=70.0, scale_down_cpu_threshold=30.0):
        self.compose_file = compose_file
        self.min_replicas = min_replicas; self.max_replicas = max_replicas
        self.scale_up_cpu_threshold = scale_up_cpu_threshold
        self.scale_down_cpu_threshold = scale_down_cpu_threshold
        self._current_replicas: Dict[str, int] = {}
        self._scale_events: List[Dict[str, Any]] = []

    def evaluate_and_scale(self, service: str, cpu_percent: float) -> Dict[str, Any]:
        current = self._current_replicas.get(service, 1)
        if cpu_percent > self.scale_up_cpu_threshold and current < self.max_replicas:
            return self.scale(service, min(current + 1, self.max_replicas),
                              reason=f"CPU={cpu_percent:.1f}% > {self.scale_up_cpu_threshold}%")
        if cpu_percent < self.scale_down_cpu_threshold and current > self.min_replicas:
            return self.scale(service, max(current - 1, self.min_replicas),
                              reason=f"CPU={cpu_percent:.1f}% < {self.scale_down_cpu_threshold}%")
        return {"service": service, "action": "no_change", "current_replicas": current,
                "cpu_percent": cpu_percent, "timestamp": datetime.utcnow().isoformat()}

    def scale(self, service: str, replicas: int, reason: str = "") -> Dict[str, Any]:
        old = self._current_replicas.get(service, 1)
        direction = "up" if replicas > old else "down"
        result = subprocess.run(
            ["docker", "compose", "-f", self.compose_file, "up", "-d",
             "--scale", f"{service}={replicas}"],
            capture_output=True, text=True, check=False)
        success = result.returncode == 0
        if success: self._current_replicas[service] = replicas
        event = {"service": service, "action": f"scale_{direction}",
                 "old_replicas": old, "new_replicas": replicas if success else old,
                 "success": success, "reason": reason, "timestamp": datetime.utcnow().isoformat()}
        self._scale_events.append(event); return event

    def get_scale_history(self, limit: int = 20): return self._scale_events[-limit:]
    def get_current_replicas(self): return dict(self._current_replicas)
