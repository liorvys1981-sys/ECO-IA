"""Resource optimiser - monitors and optimises CPU/RAM usage."""

import logging
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)


class ResourceOptimizer:
    """Monitors system resource usage and applies optimisations."""

    def __init__(self, cpu_threshold: float = 85.0, ram_threshold: float = 90.0) -> None:
        self.cpu_threshold = cpu_threshold
        self.ram_threshold = ram_threshold

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def get_metrics(self) -> Dict[str, Any]:
        """Return current CPU, RAM, and disk metrics."""
        try:
            import psutil  # type: ignore[import]

            cpu_pct = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            net = psutil.net_io_counters()
            return {
                "cpu_percent": cpu_pct,
                "ram_percent": ram.percent,
                "ram_used_gb": round(ram.used / 1024**3, 2),
                "ram_total_gb": round(ram.total / 1024**3, 2),
                "disk_percent": disk.percent,
                "disk_used_gb": round(disk.used / 1024**3, 2),
                "disk_total_gb": round(disk.total / 1024**3, 2),
                "net_bytes_sent_mb": round(net.bytes_sent / 1024**2, 2),
                "net_bytes_recv_mb": round(net.bytes_recv / 1024**2, 2),
            }
        except ImportError:
            logger.warning("psutil not installed; returning simulated metrics.")
            return self._simulate_metrics()

    def _simulate_metrics(self) -> Dict[str, Any]:
        import random

        return {
            "cpu_percent": round(random.uniform(10, 60), 1),
            "ram_percent": round(random.uniform(30, 70), 1),
            "ram_used_gb": round(random.uniform(1, 6), 2),
            "ram_total_gb": 8.0,
            "disk_percent": round(random.uniform(20, 50), 1),
            "disk_used_gb": round(random.uniform(20, 80), 2),
            "disk_total_gb": 160.0,
            "net_bytes_sent_mb": round(random.uniform(100, 5000), 2),
            "net_bytes_recv_mb": round(random.uniform(100, 5000), 2),
        }

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyse(self) -> Dict[str, Any]:
        """Analyse current resource usage and return recommendations."""
        metrics = self.get_metrics()
        recommendations = []

        if metrics["cpu_percent"] > self.cpu_threshold:
            recommendations.append(
                f"CPU usage is high ({metrics['cpu_percent']}%). Consider scaling up or optimising workloads."
            )
        if metrics["ram_percent"] > self.ram_threshold:
            recommendations.append(
                f"RAM usage is high ({metrics['ram_percent']}%). Consider adding swap or scaling RAM."
            )
        if metrics["disk_percent"] > 80:
            recommendations.append(
                f"Disk usage is high ({metrics['disk_percent']}%). Run cleanup or expand storage."
            )

        return {
            "metrics": metrics,
            "status": "warning" if recommendations else "healthy",
            "recommendations": recommendations,
        }

    def is_under_pressure(self) -> bool:
        """Return True if the system is under resource pressure."""
        metrics = self.get_metrics()
        return metrics["cpu_percent"] > self.cpu_threshold or metrics["ram_percent"] > self.ram_threshold
