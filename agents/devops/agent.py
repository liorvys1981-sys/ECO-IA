"""DevOps agent wrapper."""

from typing import Any, Dict, Optional

from core.agent_base import AgentBase

from .auto_heal import AutoHealer
from .backup import BackupManager
from .deployer import Deployer


class DevOpsAgent(AgentBase):
    def __init__(
        self,
        message_bus=None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            name="devops",
            description="Deployments, auto-healing, and backups",
            message_bus=message_bus,
            config=config,
        )
        auto_heal_config = self.get_config("auto_heal", {})
        backup_config = self.get_config("backup", {})
        self.auto_healer = AutoHealer(
            services=auto_heal_config.get("services"),
            check_interval=auto_heal_config.get("check_interval", 60),
            max_restart_attempts=auto_heal_config.get("max_restart_attempts", 3),
        )
        self.backup_manager = BackupManager(
            local_paths=backup_config.get("local_paths"),
            retention_days=backup_config.get("retention_days", 30),
        )
        self.deployer = Deployer()

    async def on_start(self) -> None:
        await self.auto_healer.start()

    async def on_stop(self) -> None:
        await self.auto_healer.stop()

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "status")

        if task_type == "status":
            return {
                "services": self.deployer.get_service_status(),
                "healer": self.auto_healer.get_history(limit=5),
                "backups": self.backup_manager.list_backups(),
            }

        if task_type == "run_backup":
            return self.backup_manager.run_backup(label=task.get("label", "manual"))

        if task_type == "deploy_service":
            return self.deployer.deploy_service(task["service"])

        if task_type == "apply_security_updates":
            return self.deployer.apply_security_updates()

        if task_type == "check_health":
            return {"results": await self.auto_healer.run_once()}

        self.tasks_failed += 1
        return {"status": "unknown_task", "task_type": task_type}
