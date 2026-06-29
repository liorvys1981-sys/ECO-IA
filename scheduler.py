"""Task scheduler for ECO-IA agents."""
import asyncio, logging
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, Optional
logger = logging.getLogger(__name__)

class ScheduledTask:
    def __init__(self, task_id, func, interval_seconds, description=""):
        self.task_id = task_id; self.func = func
        self.interval_seconds = interval_seconds; self.description = description
        self.last_run = None; self.run_count = 0; self.error_count = 0; self._task = None

class TaskScheduler:
    def __init__(self): self._tasks: Dict[str, ScheduledTask] = {}; self._running = False
    def register(self, task_id, func, interval_seconds, description=""):
        t = ScheduledTask(task_id, func, interval_seconds, description)
        self._tasks[task_id] = t; return t
    def unregister(self, task_id):
        t = self._tasks.pop(task_id, None)
        if t and t._task: t._task.cancel()
        return t is not None
    async def start(self):
        self._running = True
        for t in self._tasks.values(): t._task = asyncio.create_task(self._run_loop(t))
    async def stop(self):
        self._running = False
        for t in self._tasks.values():
            if t._task: t._task.cancel()
    async def _run_loop(self, s):
        while self._running:
            await asyncio.sleep(s.interval_seconds)
            try:
                await s.func(); s.last_run = datetime.utcnow(); s.run_count += 1
            except asyncio.CancelledError: break
            except Exception as e: s.error_count += 1; logger.error("Task '%s' error: %s", s.task_id, e)
    def list_tasks(self):
        return [{"task_id": t.task_id, "description": t.description,
                 "interval_seconds": t.interval_seconds,
                 "last_run": t.last_run.isoformat() if t.last_run else None,
                 "run_count": t.run_count, "error_count": t.error_count}
                for t in self._tasks.values()]
