"""Health and cleanup Celery tasks."""

import asyncio

from agents.devops.agent import DevOpsAgent
from agents.resources.agent import ResourcesAgent


def check_all_services() -> dict:
    devops = DevOpsAgent()
    resources = ResourcesAgent()
    return {
        "devops": asyncio.run(devops.execute({"type": "check_health"})),
        "resources": asyncio.run(resources.execute({"type": "analyse"})),
    }


def cleanup_resources() -> list[dict]:
    resources = ResourcesAgent()
    return asyncio.run(resources.execute({"type": "cleanup"}))["results"]
