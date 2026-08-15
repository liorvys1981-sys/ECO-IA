"""Backup manager for DevOps automation."""

from __future__ import annotations

import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class BackupManager:
    def __init__(
        self,
        local_paths: Optional[List[str]] = None,
        retention_days: int = 30,
        backup_root: Optional[str] = None,
    ) -> None:
        self.local_paths = local_paths or ["/opt/eco-ia/data", "/opt/eco-ia/config"]
        self.retention_days = retention_days
        self.backup_root = Path(backup_root or Path.cwd() / ".backup-artifacts")
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self._history: List[Dict[str, Any]] = []

    def run_backup(self, label: str = "daily") -> Dict[str, Any]:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"eco-ia-backup-{label}-{timestamp}-{uuid.uuid4().hex[:6]}"
        target_dir = self.backup_root / backup_name
        target_dir.mkdir(parents=True, exist_ok=True)

        copied, missing = [], []
        for source_path in self.local_paths:
            source = Path(source_path)
            if source.exists():
                destination = target_dir / source.name
                if source.is_dir():
                    shutil.copytree(source, destination, dirs_exist_ok=True)
                else:
                    shutil.copy2(source, destination)
                copied.append(str(source))
            else:
                missing.append(str(source))

        status = "success" if copied and not missing else "partial" if copied else "simulated"
        result = {
            "status": status,
            "backup_name": backup_name,
            "label": label,
            "target_dir": str(target_dir),
            "copied_paths": copied,
            "missing_paths": missing,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._history.append(result)
        self._prune_old_backups()
        return result

    def list_backups(self) -> List[Dict[str, Any]]:
        return self._history[-50:]

    def get_latest_backup(self) -> Optional[Dict[str, Any]]:
        return self._history[-1] if self._history else None

    def _prune_old_backups(self) -> None:
        cutoff = datetime.utcnow().timestamp() - (self.retention_days * 86400)
        for child in self.backup_root.iterdir():
            if child.stat().st_mtime < cutoff:
                if child.is_dir():
                    shutil.rmtree(child, ignore_errors=True)
                else:
                    child.unlink(missing_ok=True)
