"""Backup manager for ECO-IA."""

from datetime import datetime
from typing import Any


class BackupManager:
    def __init__(self, local_paths: list[str] | None = None, retention_days: int = 30):
        self.local_paths = local_paths or ["/opt/eco-ia/data", "/opt/eco-ia/config"]
        self.retention_days = retention_days
        self._history: list[dict[str, Any]] = []

    def run_backup(self, label: str = "manual") -> dict[str, Any]:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        result = {
            "backup_name": f"eco-ia-backup-{label}-{timestamp}",
            "status": "simulated",
            "label": label,
            "paths": self.local_paths,
            "retention_days": self.retention_days,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._history.append(result)
        return result

    def list_backups(self) -> list[dict[str, Any]]:
        return list(self._history)

    def get_latest_backup(self) -> dict[str, Any] | None:
        return self._history[-1] if self._history else None
