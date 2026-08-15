"""Analytics agent wrapper."""

from typing import Any, Dict, Optional

from core.agent_base import AgentBase

from .dashboard import DashboardData
from .predictor import Predictor
from .reporter import Reporter


class AnalyticsAgent(AgentBase):
    def __init__(
        self,
        message_bus=None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            name="analytics",
            description="Reporting, anomaly detection, and dashboard metrics",
            message_bus=message_bus,
            config=config,
        )
        predictor_config = self.get_config("predictor", {})
        self.predictor = Predictor(
            window_size=predictor_config.get("window_size", 20),
            z_score_threshold=predictor_config.get("z_score_threshold", 2.5),
        )
        self.dashboard = DashboardData()
        self.reporter = Reporter()

    async def on_start(self) -> None:
        return None

    async def on_stop(self) -> None:
        return None

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "kpis")

        if task_type == "record_metric":
            self.predictor.record(task["metric"], task["value"])
            return {"status": "recorded"}

        if task_type == "check_metric":
            alert = self.predictor.check_and_alert(task["metric"], task["value"])
            return {"alert": alert}

        if task_type == "snapshot":
            return self.dashboard.snapshot(
                resources=task.get("resources"),
                monetization=task.get("monetization"),
                security=task.get("security"),
                devops=task.get("devops"),
            )

        if task_type == "daily_report":
            return self.reporter.generate_daily_report(task.get("data", {}))

        if task_type == "kpis":
            return self.dashboard.get_kpis()

        self.tasks_failed += 1
        return {"status": "unknown_task", "task_type": task_type}
