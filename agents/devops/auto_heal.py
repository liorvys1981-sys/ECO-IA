"""Auto-healer - monitors services and automatically restarts failed ones."""

import asyncio
import logging
import subprocess
from collections.abc import Callable, Coroutine
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class AutoHealer:
    """Monitors Docker services and restarts them when they become unhealthy."""

    def __init__(
        self,
        services: list[str] | None = None,
        check_interval: int = 60,
        max_restart_attempts: int = 3,
        on_failure: Callable[[str, int], Coroutine[Any, Any, None]] | None = None,
    ) -> None:
        self.services = services or []
        self.check_interval = check_interval
        self.max_restart_attempts = max_restart_attempts
        self._on_failure = on_failure
        self._restart_counts: dict[str, int] = {}
        self._heal_log: list[dict[str, Any]] = []
        self._running = False
        self._monitor_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self._running = True
        logger.info("AutoHealer started. Monitoring %d service(s).", len(self.services))
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop(self) -> None:
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            await asyncio.gather(self._monitor_task, return_exceptions=True)
            self._monitor_task = None
        logger.info("AutoHealer stopped.")

    async def _monitor_loop(self) -> None:
        while self._running:
            for service in self.services:
                await self._check_and_heal(service)
            await asyncio.sleep(self.check_interval)

    async def _check_and_heal(self, service: str) -> dict[str, Any]:
        status = self._get_service_status(service)
        if status in ("running", "healthy"):
            self._restart_counts[service] = 0
            return {
                "service": service,
                "status_before": status,
                "restart_attempt": 0,
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
            }

        attempts = self._restart_counts.get(service, 0)
        logger.warning(
            "Service '%s' is '%s'. Attempt %d/%d.",
            service,
            status,
            attempts + 1,
            self.max_restart_attempts,
        )

        if attempts >= self.max_restart_attempts:
            logger.error(
                "Max restart attempts reached for '%s'. Manual intervention required.",
                service,
            )
            if self._on_failure:
                await self._on_failure(service, attempts)
            record = {
                "service": service,
                "status_before": status,
                "restart_attempt": attempts,
                "success": False,
                "timestamp": datetime.utcnow().isoformat(),
            }
            self._heal_log.append(record)
            return record

        result = self._restart_service(service)
        self._restart_counts[service] = attempts + 1
        record = {
            "service": service,
            "status_before": status,
            "restart_attempt": attempts + 1,
            "success": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._heal_log.append(record)
        return record

    def _get_service_status(self, service: str) -> str:
        try:
            result = subprocess.run(  # noqa: S603
                ["docker", "inspect", "--format", "{{.State.Status}}", service],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip() or "unknown"
        except FileNotFoundError:
            return "docker_not_found"

    def _restart_service(self, service: str) -> bool:
        try:
            result = subprocess.run(  # noqa: S603
                ["docker", "restart", service],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                logger.info("Service '%s' restarted successfully.", service)
                return True
            logger.error("Failed to restart '%s': %s", service, result.stderr)
            return False
        except FileNotFoundError:
            logger.error("docker command not found.")
            return False

    async def run_once(self) -> list[dict[str, Any]]:
        return [await self._check_and_heal(service) for service in self.services]

    def get_heal_log(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._heal_log[-limit:]

    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.get_heal_log(limit)

    def get_stats(self) -> dict[str, Any]:
        return {
            "monitored_services": self.services,
            "total_heal_events": len(self._heal_log),
            "restart_counts": dict(self._restart_counts),
        }
