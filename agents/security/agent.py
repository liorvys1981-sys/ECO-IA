"""Security agent wrapper."""

from typing import Any

from core.agent_base import AgentBase

from .auditor import SecurityAuditor
from .firewall import FirewallManager
from .intrusion_detector import IntrusionDetector


class SecurityAgent(AgentBase):
    supported_task_types = (
        "security_task",
        "analyse_auth_log",
        "audit",
        "block_ip",
    )

    def __init__(
        self,
        message_bus=None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            name="security",
            description="Firewalling, intrusion detection, and audits",
            message_bus=message_bus,
            config=config,
        )
        intrusion_config = self.get_config("intrusion_detector", {})
        self.firewall = FirewallManager()
        self.detector = IntrusionDetector(
            threshold_minutes=intrusion_config.get("threshold_minutes", 5),
            brute_force_threshold=intrusion_config.get("brute_force_threshold", 10),
        )
        self.auditor = SecurityAuditor()

    async def on_start(self) -> None:
        return None

    async def on_stop(self) -> None:
        return None

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        task_type = task.get("type", "summary")

        if task_type == "analyse_auth_log":
            return {"threats": self.detector.analyse_auth_log()}

        if task_type == "audit":
            return self.auditor.run_full_audit()

        if task_type == "block_ip":
            return self.firewall.block_ip(task["ip"], task.get("reason", ""))

        if task_type == "summary":
            return {
                "alerts": self.detector.get_summary(),
                "firewall": self.firewall.get_status(),
            }

        self.tasks_failed += 1
        return {"status": "unknown_task", "task_type": task_type}

    async def on_message(self, message) -> None:
        await super().on_message(message)
        if message.content.get("type") == "audit_request":
            result = self.auditor.run_full_audit()
            await self.send_message(
                "orchestrator",
                {"type": "alert", "message": "Security audit completed", "audit": result},
            )
