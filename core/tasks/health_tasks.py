"""Health and cleanup Celery tasks."""

from agents.resources.cleaner import Cleaner
from agents.resources.optimizer import ResourceOptimizer


def check_all_services() -> dict:
    optimizer = ResourceOptimizer()
    return optimizer.analyse()


def cleanup_resources() -> list[dict]:
    cleaner = Cleaner(temp_dirs=[])
    return cleaner.run_all()
