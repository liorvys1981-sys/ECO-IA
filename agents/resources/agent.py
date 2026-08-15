"""Resources agent wrapper."""

from typing import Any

from core.agent_base import AgentBase

from .cleaner import Cleaner
from .optimizer import ResourceOptimizer
from .scaler import AutoScaler


class ResourcesAgent(AgentBase):
    def __init__(
        self,
        message_bus=None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            name="resources",
            description="Resource optimization, scaling, and cleanup",
            message_bus=message_bus,
            config=config,
        )
        optimizer_config = self.get_config("optimizer", {})
        scaler_config = self.get_config("scaler", {})
        cleaner_config = self.get_config("cleaner", {})
        self.optimizer = ResourceOptimizer(
            cpu_threshold=optimizer_config.get("cpu_threshold", 85.0),
            ram_threshold=optimizer_config.get("ram_threshold", 90.0),
        )
        self.scaler = AutoScaler(
            min_replicas=scaler_config.get("min_replicas", 1),
            max_replicas=scaler_config.get("max_replicas", 10),
            scale_up_cpu_threshold=scaler_config.get("scale_up_cpu_threshold", 70.0),
            scale_down_cpu_threshold=scaler_config.get("scale_down_cpu_threshold", 30.0),
        )
        self.cleaner = Cleaner(
            max_log_age_days=cleaner_config.get("max_log_age_days", 7),
            max_log_size_mb=cleaner_config.get("max_log_size_mb", 100.0),
        )

    async def on_start(self) -> None:
        return None

    async def on_stop(self) -> None:
        return None

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        task_type = task.get("type", "analyse")

        if task_type == "metrics":
            return self.optimizer.get_metrics()

        if task_type == "analyse":
            return self.optimizer.analyse()

        if task_type == "scale":
            return self.scaler.evaluate_and_scale(task["service"], task["cpu_percent"])

        if task_type == "cleanup":
            return {"results": self.cleaner.run_all()}

        self.tasks_failed += 1
        return {"status": "unknown_task", "task_type": task_type}
