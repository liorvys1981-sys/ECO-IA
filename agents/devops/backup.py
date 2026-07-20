"""Backup manager aligned with the repository backup script."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any


class BackupManager:
    def __init__(
        self,
        eco_ia_dir: str | None = None,
        local_backup_dir: str | None = None,
        retention_days: int | None = None,
    ):
        self.eco_ia_dir = eco_ia_dir or os.getenv("ECO_IA_DIR", "/opt/eco-ia")
        self.local_backup_dir = local_backup_dir or os.getenv("LOCAL_BACKUP_DIR")
        self.retention_days = retention_days or int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
        self.script_path = Path(__file__).resolve().parents[2] / "backup.sh"
        self.remote_host = os.getenv("HETZNER_STORAGE_BOX_HOST", "")
        self.remote_user = os.getenv("HETZNER_STORAGE_BOX_USER", "")
        self._history: list[dict[str, Any]] = []

    def run_backup(self, label: str = "manual") -> dict[str, Any]:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        result = {
            "backup_name": f"eco-ia-backup-{label}-{timestamp}",
            "status": "simulated",
            "label": label,
            "eco_ia_dir": self.eco_ia_dir,
            "local_backup_dir": self.local_backup_dir,
            "retention_days": self.retention_days,
            "uses_temp_dir": not bool(self.local_backup_dir),
            "script_path": str(self.script_path),
            "remote_path": (
                f"{self.remote_user}@{self.remote_host}:/backups/eco-ia"
                if self.remote_host and self.remote_user
                else None
            ),
            "created_at": datetime.utcnow().isoformat(),
        }
        self._history.append(result)
        return result

    def list_backups(self) -> list[dict[str, Any]]:
        return list(self._history)

    def get_latest_backup(self) -> dict[str, Any] | None:
        return self._history[-1] if self._history else None
