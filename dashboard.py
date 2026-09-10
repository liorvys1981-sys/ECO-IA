"""Dashboard data aggregator for the analytics agent."""

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


class DashboardData:
    """Aggregates metrics from all agents for the Grafana/web dashboard."""

    def __init__(self) -> None:
        self._snapshots: list[dict[str, Any]] = []

    def snapshot(
        self,
        resources: dict[str, Any] | None = None,
        monetization: dict[str, Any] | None = None,
        security: dict[str, Any] | None = None,
        devops: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Capture a dashboard snapshot from agent data."""
        snap = {
            "timestamp": datetime.now(UTC).isoformat(),
            "resources": resources or {},
            "monetization": monetization or {},
            "security": security or {},
            "devops": devops or {},
        }
        self._snapshots.append(snap)
        if len(self._snapshots) > 1440:  # keep ~24h at 1-min intervals
            self._snapshots = self._snapshots[-1440:]
        return snap

    def get_latest(self) -> dict[str, Any] | None:
        return self._snapshots[-1] if self._snapshots else None

    def get_history(self, limit: int = 60) -> list[dict[str, Any]]:
        return self._snapshots[-limit:]

    def get_kpis(self) -> dict[str, Any]:
        """Compute high-level KPIs from the latest snapshot."""
        latest = self.get_latest()
        if not latest:
            return {"status": "no_data"}

        mon = latest.get("monetization", {})
        res = latest.get("resources", {})
        sec = latest.get("security", {})

        return {
            "timestamp": latest["timestamp"],
            "active_clients": mon.get("active_clients", 0),
            "monthly_revenue_usd": mon.get("monthly_revenue_usd", 0.0),
            "cpu_percent": res.get("cpu_percent", 0.0),
            "ram_percent": res.get("ram_percent", 0.0),
            "disk_percent": res.get("disk_percent", 0.0),
            "security_alerts": sec.get("total_alerts", 0),
            "system_health": self._compute_health(res, sec),
        }

    def _compute_health(self, resources: dict[str, Any], security: dict[str, Any]) -> str:
        if security.get("high_severity", 0) > 0:
            return "critical"
        cpu = resources.get("cpu_percent", 0)
        ram = resources.get("ram_percent", 0)
        if cpu > 90 or ram > 90:
            return "warning"
        return "healthy"
