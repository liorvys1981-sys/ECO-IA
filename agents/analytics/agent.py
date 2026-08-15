"""Analytics agent wrapper."""

from typing import Any

from core.agent_base import AgentBase

from .dashboard import DashboardData
from .predictor import Predictor
from .reporter import Reporter


class AnalyticsAgent(AgentBase):
    supported_task_types = (
        "analytics_task",
        "record_metric",
        "check_metric",
        "snapshot",
        "daily_report",
        "kpis",
    )

    def __init__(
        self,
        message_bus=None,
        config: dict[str, Any] | None = None,
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
        self._cpu_history: list[float] = []
        self._ram_history: list[float] = []

    async def on_start(self) -> None:
        return None

    async def on_stop(self) -> None:
        return None

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        task_type = task.get("type", "summary")

        if task_type in {"analytics_task", "summary"}:
            business_metrics = self.dashboard.get_kpis()
            report = self.reporter.generate_daily_report(business_metrics)
            return {
                "business_metrics": business_metrics,
                "anomalies": await self._detect_anomalies(),
                "report_generated": report["type"] == "daily",
            }

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

    def record_metrics(self, cpu_percent: float, ram_percent: float) -> None:
        self._cpu_history.append(cpu_percent)
        self._ram_history.append(ram_percent)
        self.predictor.record("cpu", cpu_percent)
        self.predictor.record("ram", ram_percent)

    async def _detect_anomalies(self) -> list[dict[str, Any]]:
        anomalies: list[dict[str, Any]] = []
        for resource_name, history in (
            ("cpu", self._cpu_history),
            ("ram", self._ram_history),
        ):
            if len(history) < self.predictor.window_size:
                continue
            is_anomaly, z_score = self.predictor.is_anomaly(resource_name, history[-1])
            if is_anomaly:
                anomalies.append(
                    {
                        "resource": resource_name,
                        "value": history[-1],
                        "z_score": z_score,
                    }
                )
        return anomalies
