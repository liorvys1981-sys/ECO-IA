"""Intrusion detector - analyses logs for suspicious activity."""

import logging
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)

# Common brute-force pattern in auth logs
_FAILED_SSH_RE = re.compile(r"Failed password for .+ from (\d+\.\d+\.\d+\.\d+)")
_INVALID_USER_RE = re.compile(r"Invalid user \S+ from (\d+\.\d+\.\d+\.\d+)")
_PORT_SCAN_THRESHOLD = 20       # unique ports in 1 minute → likely scan
_BRUTE_FORCE_THRESHOLD = 10     # failed logins from single IP → brute force


class IntrusionDetector:
    """Analyses system logs to detect and report intrusion attempts."""

    def __init__(
        self,
        auth_log_path: str = "/var/log/auth.log",
        threshold_minutes: int = 5,
        brute_force_threshold: int = _BRUTE_FORCE_THRESHOLD,
    ) -> None:
        self.auth_log_path = auth_log_path
        self.threshold_minutes = threshold_minutes
        self.brute_force_threshold = brute_force_threshold
        self._alerts: List[Dict[str, Any]] = []
        self._blocked_ips: List[str] = []

    # ------------------------------------------------------------------
    # Log analysis
    # ------------------------------------------------------------------

    def analyse_auth_log(self) -> List[Dict[str, Any]]:
        """Parse auth.log and return detected threats."""
        threats = []
        log_path = Path(self.auth_log_path)
        if not log_path.exists():
            logger.warning("Auth log not found at '%s'. Skipping.", self.auth_log_path)
            return []

        ip_fail_counts: Counter = Counter()
        try:
            with log_path.open(errors="replace") as fh:
                for line in fh:
                    for pattern in (_FAILED_SSH_RE, _INVALID_USER_RE):
                        m = pattern.search(line)
                        if m:
                            ip_fail_counts[m.group(1)] += 1
        except OSError as exc:
            logger.error("Could not read auth log: %s", exc)
            return []

        for ip, count in ip_fail_counts.items():
            if count >= self.brute_force_threshold:
                threat = {
                    "type": "brute_force",
                    "ip": ip,
                    "failed_attempts": count,
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "high" if count >= self.brute_force_threshold * 2 else "medium",
                }
                threats.append(threat)
                self._alerts.append(threat)
                logger.warning("Brute-force detected from %s (%d attempts).", ip, count)

        return threats

    # ------------------------------------------------------------------
    # Threat management
    # ------------------------------------------------------------------

    def get_suspicious_ips(self) -> List[str]:
        """Return IPs that triggered alerts."""
        return list({a["ip"] for a in self._alerts if "ip" in a})

    def get_alerts(self, severity: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        alerts = self._alerts
        if severity:
            alerts = [a for a in alerts if a.get("severity") == severity]
        return alerts[-limit:]

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_alerts": len(self._alerts),
            "high_severity": sum(1 for a in self._alerts if a.get("severity") == "high"),
            "medium_severity": sum(1 for a in self._alerts if a.get("severity") == "medium"),
            "suspicious_ips": self.get_suspicious_ips(),
        }
