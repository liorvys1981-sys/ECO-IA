"""Dynamic firewall management using UFW."""

import ipaddress
import logging
import shutil
import subprocess
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


def _is_valid_ip(ip: str) -> bool:
    try:
        if "/" in ip:
            ipaddress.IPv4Network(ip, strict=False)
        else:
            ipaddress.IPv4Address(ip)
    except ValueError:
        return False
    return True


class FirewallManager:
    def __init__(self) -> None:
        self._blocked_ips: list[str] = []
        self._rule_log: list[dict[str, Any]] = []

    def _ufw(self, *args: str) -> dict[str, Any]:
        cmd = ["ufw", *args]
        logger.debug("UFW: %s", " ".join(cmd))

        if shutil.which("ufw") is None:
            return {
                "cmd": " ".join(cmd),
                "returncode": 127,
                "stdout": "",
                "stderr": "ufw executable not found",
            }

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)  # noqa: S603
        except OSError as exc:
            return {
                "cmd": " ".join(cmd),
                "returncode": 127,
                "stdout": "",
                "stderr": str(exc),
            }

        return {
            "cmd": " ".join(cmd),
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    def _record_rule(self, action: str, **details: Any) -> dict[str, Any]:
        record = {
            "action": action,
            **details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._rule_log.append(record)
        return record

    def block_ip(self, ip: str, reason: str = "") -> dict[str, Any]:
        if not _is_valid_ip(ip):
            raise ValueError(f"Invalid IP: {ip!r}")
        result = self._ufw("deny", "from", ip, "to", "any")
        record = self._record_rule(
            "block",
            "ip": ip,
            "reason": reason,
            "success": result["returncode"] == 0,
        )
        if record["success"] and ip not in self._blocked_ips:
            self._blocked_ips.append(ip)
        logger.info("Blocked IP '%s'. Reason: %s", ip, reason)
        return record

    def unblock_ip(self, ip: str) -> dict[str, Any]:
        if not _is_valid_ip(ip):
            raise ValueError(f"Invalid IP: {ip!r}")
        result = self._ufw("delete", "deny", "from", ip, "to", "any")
        record = self._record_rule(
            "unblock",
            ip=ip,
            success=result["returncode"] == 0,
        )
        if record["success"] and ip in self._blocked_ips:
            self._blocked_ips.remove(ip)
        logger.info("Unblocked IP '%s'.", ip)
        return record

    def allow_port(self, port: int, protocol: str = "tcp") -> dict[str, Any]:
        if not (1 <= port <= 65535):
            raise ValueError(f"Invalid port: {port}")
        if protocol not in ("tcp", "udp"):
            raise ValueError(f"Invalid protocol: {protocol!r}")
        result = self._ufw("allow", f"{port}/{protocol}")
        record = self._record_rule(
            "allow_port",
            port=port,
            protocol=protocol,
            success=result["returncode"] == 0,
        )
        logger.info("Allowed %s/%s.", port, protocol)
        return record

    def deny_port(self, port: int, protocol: str = "tcp") -> dict[str, Any]:
        if not (1 <= port <= 65535):
            raise ValueError(f"Invalid port: {port}")
        if protocol not in ("tcp", "udp"):
            raise ValueError(f"Invalid protocol: {protocol!r}")
        result = self._ufw("deny", f"{port}/{protocol}")
        record = self._record_rule(
            "deny_port",
            port=port,
            protocol=protocol,
            success=result["returncode"] == 0,
        )
        logger.info("Denied %s/%s.", port, protocol)
        return record

    def get_status(self) -> dict[str, Any]:
        result = self._ufw("status", "numbered")
        return {
            "ufw_output": result["stdout"],
            "blocked_ips": list(self._blocked_ips),
            "total_rules": len(self._rule_log),
        }

    def get_rule_log(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._rule_log[-limit:]
