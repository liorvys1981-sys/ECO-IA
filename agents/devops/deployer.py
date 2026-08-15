"""Docker Compose deployment helper."""

import subprocess
from datetime import datetime
from typing import Any, Dict, List


class Deployer:
    def __init__(self, compose_file: str = "docker/docker-compose.yml") -> None:
        self.compose_file = compose_file
        self._events: List[Dict[str, Any]] = []

    def deploy_service(self, service: str) -> Dict[str, Any]:
        result = subprocess.run(
            ["docker", "compose", "-f", self.compose_file, "up", "-d", service],
            capture_output=True,
            text=True,
            check=False,
        )
        event = {
            "action": "deploy_service",
            "service": service,
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._events.append(event)
        return event

    def apply_security_updates(self) -> Dict[str, Any]:
        result = subprocess.run(
            ["docker", "compose", "-f", self.compose_file, "pull"],
            capture_output=True,
            text=True,
            check=False,
        )
        event = {
            "action": "apply_security_updates",
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._events.append(event)
        return event

    def get_service_status(self) -> Dict[str, Any]:
        result = subprocess.run(
            ["docker", "compose", "-f", self.compose_file, "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "status": "operational" if result.returncode == 0 else "degraded",
            "compose_file": self.compose_file,
            "output": result.stdout.strip(),
            "timestamp": datetime.utcnow().isoformat(),
        }
