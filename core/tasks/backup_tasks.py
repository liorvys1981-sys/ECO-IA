"""Backup-related Celery tasks."""

import asyncio

from agents.devops.agent import DevOpsAgent


def run_backup(label: str = "hourly") -> dict:
    agent = DevOpsAgent()
    return asyncio.run(agent.execute({"type": "run_backup", "label": label}))
