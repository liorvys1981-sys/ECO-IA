"""Backup-related Celery tasks."""

from agents.devops.backup import BackupManager


def run_backup(label: str = "hourly") -> dict:
    manager = BackupManager()
    return manager.run_backup(label=label)
