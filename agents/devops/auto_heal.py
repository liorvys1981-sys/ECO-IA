"""Auto-healer for Docker services."""

from __future__ import annotations

import asyncio
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional


class AutoHealer:
    def __init__(
        self,
        services: Optional[List[str]] = None,
        check_interval: int = 60,
        max_restart_attempts: int = 3,
    ) -> None:
        self.services = services or ["eco-ia-api", "eco-ia-worker", "eco-ia-postgres"]
        self.check_interval = check_interval
        self.max_restart_attempts = max_restart_attempts
        self.restart_counts: Dict[str, int] = {}
        self._history: List[Dict[str, Any]] = []
        self._running = False

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    async def tick(self) -> List[Dict[str, Any]]:
        return [self.check_service(service) for service in self.services]

    async def run_once(self) -> List[Dict[str, Any]]:
        return await self.tick()

    def check_service(self, service: str) -> Dict[str, Any]:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", service],
            capture_output=True,
            text=True,
            check=False,
        )
        status = result.stdout.strip() if result.returncode == 0 else "unknown"
        healthy = status in {"running", "healthy"}
        event = {
            "service": service,
            "status": status,
            "healthy": healthy,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if not healthy:
            event["restart"] = self.restart_service(service)
        self._history.append(event)
        return event

    def restart_service(self, service: str) -> Dict[str, Any]:
        attempts = self.restart_counts.get(service, 0)
        if attempts >= self.max_restart_attempts:
            return {"status": "skipped", "reason": "max_restart_attempts_reached"}

        result = subprocess.run(
            ["docker", "restart", service],
            capture_output=True,
            text=True,
            check=False,
        )
        self.restart_counts[service] = attempts + 1
        return {
            "status": "restarted" if result.returncode == 0 else "failed",
            "attempt": self.restart_counts[service],
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._history[-limit:]
