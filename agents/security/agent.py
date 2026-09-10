"""Security agent wrapper."""

from pathlib import Path
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
        self._blocked_ips = self.firewall._blocked_ips  # noqa: SLF001
        self._failed_attempts: dict[str, int] = {}

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
            result = self.firewall.block_ip(task["ip"], task.get("reason", ""))
            self._blocked_ips = self.firewall._blocked_ips  # noqa: SLF001
            return result

        if task_type == "summary":
            log_scan = await self._scan_auth_logs()
            audit = await self._run_audit()
            return {
                "log_scan": log_scan,
                "blocked": list(self._blocked_ips),
                "audit": audit,
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

    async def _scan_journalctl(self) -> dict[str, Any]:
        failed_logins = self.auditor.check_failed_logins()
        return {
            "suspicious_lines": failed_logins.get("count", 0),
            "source": "journalctl",
        }

    async def _scan_auth_logs(self) -> dict[str, Any]:
        if not Path(self.detector.auth_log_path).exists():
            return await self._scan_journalctl()

        threats = self.detector.analyse_auth_log()
        suspicious_ips = self.detector.get_suspicious_ips()
        self._failed_attempts = {
            threat["ip"]: threat["failed_attempts"]
            for threat in threats
            if threat.get("ip") and threat.get("failed_attempts") is not None
        }
        return {
            "suspicious_ips": len(suspicious_ips),
            "newly_blocked": [],
            "source": "auth.log",
        }

    async def _run_audit(self) -> dict[str, Any]:
        return self.auditor.run_full_audit()
