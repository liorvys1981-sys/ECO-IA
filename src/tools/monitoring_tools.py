"""Monitoring helpers exposed to agents."""

from agents.analytics.dashboard import DashboardData
from agents.resources.optimizer import ResourceOptimizer


class MonitoringTools:
    """Helpers for collecting resource and KPI snapshots."""

    def __init__(self) -> None:
        self.optimizer = ResourceOptimizer()
        self.dashboard = DashboardData()

    def resource_snapshot(self) -> dict:
        return self.optimizer.get_metrics()

    def business_snapshot(self) -> dict:
        return self.dashboard.get_kpis()


__all__ = ["MonitoringTools"]
