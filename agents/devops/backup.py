"""Backup manager - automated backups to Hetzner Storage Box."""

import logging
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class BackupManager:
    """Handles automated backups to Hetzner Storage Box via rsync/SSH."""

    def __init__(
        self,
        storage_box_host: str | None = None,
        storage_box_user: str | None = None,
        remote_path: str = "/backups/eco-ia",
        local_paths: list[str] | None = None,
        retention_days: int = 30,
    ) -> None:
        self.storage_box_host = storage_box_host or os.getenv("HETZNER_STORAGE_BOX_HOST", "")
        self.storage_box_user = storage_box_user or os.getenv("HETZNER_STORAGE_BOX_USER", "")
        self.remote_path = remote_path
        self.local_paths = local_paths or ["/opt/eco-ia/data", "/opt/eco-ia/config"]
        self.retention_days = retention_days
        self._backup_history: list[dict[str, Any]] = []

    def run_backup(self, label: str = "") -> dict[str, Any]:
        """Perform a full rsync backup to Hetzner Storage Box."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}" + (f"_{label}" if label else "")
        remote_target = (
            f"{self.storage_box_user}@{self.storage_box_host}:{self.remote_path}/{backup_name}/"
        )

        if not self.storage_box_host:
            logger.warning("HETZNER_STORAGE_BOX_HOST not set; simulating backup.")
            record = self._simulate_backup(backup_name)
            self._backup_history.append(record)
            return record

        results = []
        for local_path in self.local_paths:
            if not Path(local_path).exists():
                logger.warning("Local path '%s' does not exist; skipping.", local_path)
                continue

            cmd = [
                "rsync",
                "-az",
                "--delete",
                "-e",
                "ssh -o StrictHostKeyChecking=no -p 23",
                local_path,
                remote_target,
            ]
            logger.info("Backing up '%s' → %s", local_path, remote_target)
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)  # noqa: S603
            results.append(
                {
                    "path": local_path,
                    "success": proc.returncode == 0,
                    "stderr": proc.stderr[-300:] if proc.stderr else "",
                }
            )

        record: dict[str, Any] = {
            "backup_name": backup_name,
            "timestamp": datetime.now(UTC).isoformat(),
            "remote_target": remote_target,
            "results": results,
            "status": "success" if all(r["success"] for r in results) else "partial",
        }
        self._backup_history.append(record)
        logger.info("Backup '%s' completed: %s", backup_name, record["status"])
        return record

    def _simulate_backup(self, backup_name: str) -> dict[str, Any]:
        return {
            "backup_name": backup_name,
            "timestamp": datetime.now(UTC).isoformat(),
            "remote_target": "simulated",
            "results": [{"path": path, "success": True, "stderr": ""} for path in self.local_paths],
            "status": "simulated",
        }

    def list_backups(self) -> list[dict[str, Any]]:
        return list(self._backup_history)

    def get_latest_backup(self) -> dict[str, Any] | None:
        return self._backup_history[-1] if self._backup_history else None
