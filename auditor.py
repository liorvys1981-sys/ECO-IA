"""Security auditor - runs periodic security checks and generates reports."""

import logging
import subprocess
from datetime import datetime
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


class SecurityAuditor:
    """Performs periodic security audits on the server."""

    def __init__(self) -> None:
        self._audit_history: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Audit checks
    # ------------------------------------------------------------------

    def check_open_ports(self) -> Dict[str, Any]:
        """List open ports using ss."""
        result = subprocess.run(  # noqa: S603
            ["ss", "-tlnp"],
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "check": "open_ports",
            "output": result.stdout,
            "success": result.returncode == 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def check_failed_logins(self) -> Dict[str, Any]:
        """Count failed login attempts in the last 24 hours using journalctl."""
        result = subprocess.run(  # noqa: S603
            ["journalctl", "-u", "ssh", "--since", "24 hours ago", "--no-pager", "-q"],
            capture_output=True,
            text=True,
            check=False,
        )
        lines = result.stdout.splitlines() if result.stdout else []
        failed = [l for l in lines if "Failed" in l or "Invalid" in l]  # noqa: E741
        return {
            "check": "failed_logins",
            "count": len(failed),
            "severity": "high" if len(failed) > 50 else "low",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def check_sudo_usage(self) -> Dict[str, Any]:
        """Audit recent sudo usage."""
        result = subprocess.run(  # noqa: S603
            ["journalctl", "-u", "sudo", "--since", "24 hours ago", "--no-pager", "-q"],
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "check": "sudo_usage",
            "events": len(result.stdout.splitlines()) if result.stdout else 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def check_world_writable_files(self, path: str = "/opt/eco-ia") -> Dict[str, Any]:
        """Find world-writable files in the ECO-IA directory."""
        result = subprocess.run(  # noqa: S603
            ["find", path, "-perm", "-o+w", "-not", "-type", "l"],
            capture_output=True,
            text=True,
            check=False,
        )
        files = [f for f in result.stdout.splitlines() if f]
        return {
            "check": "world_writable_files",
            "files": files,
            "count": len(files),
            "severity": "high" if files else "low",
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ------------------------------------------------------------------
    # Full audit
    # ------------------------------------------------------------------

    def run_full_audit(self) -> Dict[str, Any]:
        """Run all security checks and aggregate results."""
        checks = [
            self.check_open_ports(),
            self.check_failed_logins(),
            self.check_sudo_usage(),
        ]
        high_severity = [c for c in checks if c.get("severity") == "high"]
        audit = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
            "overall_status": "alert" if high_severity else "ok",
            "high_severity_count": len(high_severity),
        }
        self._audit_history.append(audit)
        logger.info("Security audit completed. Status: %s", audit["overall_status"])
        return audit

    def get_audit_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._audit_history[-limit:]
