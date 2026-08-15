"""Task scheduler for ECO-IA agents."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class ScheduledTask:
    def __init__(
        self,
        task_id: str,
        func: Callable[[], Awaitable[None]],
        interval_seconds: int,
        description: str = "",
    ) -> None:
        self.task_id = task_id
        self.func = func
        self.interval_seconds = interval_seconds
        self.description = description
        self.last_run: datetime | None = None
        self.run_count = 0
        self.error_count = 0
        self._task: asyncio.Task[None] | None = None


class TaskScheduler:
    def __init__(self) -> None:
        self._tasks: dict[str, ScheduledTask] = {}
        self._running = False

    def register(
        self,
        task_id: str,
        func: Callable[[], Awaitable[None]],
        interval_seconds: int,
        description: str = "",
    ) -> ScheduledTask:
        scheduled = ScheduledTask(task_id, func, interval_seconds, description)
        self._tasks[task_id] = scheduled
        if self._running:
            scheduled._task = asyncio.create_task(self._run_loop(scheduled))
        return scheduled

    def unregister(self, task_id: str) -> bool:
        scheduled = self._tasks.pop(task_id, None)
        if scheduled and scheduled._task:
            scheduled._task.cancel()
        return scheduled is not None

    async def start(self) -> None:
        self._running = True
        for scheduled in self._tasks.values():
            if scheduled._task is None or scheduled._task.done():
                scheduled._task = asyncio.create_task(self._run_loop(scheduled))

    async def stop(self) -> None:
        self._running = False
        for scheduled in self._tasks.values():
            if scheduled._task:
                scheduled._task.cancel()
        await asyncio.gather(
            *(task._task for task in self._tasks.values() if task._task),
            return_exceptions=True,
        )

    async def _run_loop(self, scheduled: ScheduledTask) -> None:
        while self._running:
            await asyncio.sleep(scheduled.interval_seconds)
            try:
                await scheduled.func()
                scheduled.last_run = datetime.utcnow()
                scheduled.run_count += 1
            except asyncio.CancelledError:
                break
            except Exception as exc:  # noqa: BLE001
                scheduled.error_count += 1
                logger.error("Task '%s' error: %s", scheduled.task_id, exc)

    def list_tasks(self) -> list[dict[str, Any]]:
        return [
            {
                "task_id": task.task_id,
                "description": task.description,
                "interval_seconds": task.interval_seconds,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "run_count": task.run_count,
                "error_count": task.error_count,
            }
            for task in self._tasks.values()
        ]
