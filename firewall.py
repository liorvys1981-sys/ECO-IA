"""Dynamic firewall management using UFW."""
import logging, re, subprocess
from datetime import datetime
from typing import Any, Dict, List
logger = logging.getLogger(__name__)

_IP_RE = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(/(\d{1,2}))?$")

def _is_valid_ip(ip: str) -> bool:
    m = _IP_RE.match(ip)
    if not m: return False
    if any(int(m.group(i)) > 255 for i in (1, 2, 3, 4)): return False
    if m.group(6) is not None and int(m.group(6)) > 32: return False
    return True

class FirewallManager:
    def __init__(self): self._blocked_ips: List[str] = []; self._rule_log: List[Dict[str, Any]] = []
    def _ufw(self, *args):
        cmd = ["ufw", *args]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {"cmd": " ".join(cmd), "returncode": r.returncode,
                "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}
    def block_ip(self, ip: str, reason: str = "") -> Dict[str, Any]:
        if not _is_valid_ip(ip): raise ValueError(f"Invalid IP: {ip!r}")
        r = self._ufw("deny", "from", ip, "to", "any")
        rec = {"action": "block", "ip": ip, "reason": reason,
               "success": r["returncode"] == 0, "timestamp": datetime.utcnow().isoformat()}
        if rec["success"] and ip not in self._blocked_ips: self._blocked_ips.append(ip)
        self._rule_log.append(rec); return rec
    def unblock_ip(self, ip: str) -> Dict[str, Any]:
        if not _is_valid_ip(ip): raise ValueError(f"Invalid IP: {ip!r}")
        r = self._ufw("delete", "deny", "from", ip, "to", "any")
        rec = {"action": "unblock", "ip": ip, "success": r["returncode"] == 0,
               "timestamp": datetime.utcnow().isoformat()}
        if rec["success"] and ip in self._blocked_ips: self._blocked_ips.remove(ip)
        self._rule_log.append(rec); return rec
    def allow_port(self, port: int, protocol: str = "tcp") -> Dict[str, Any]:
        if not (1 <= port <= 65535): raise ValueError(f"Invalid port: {port}")
        if protocol not in ("tcp", "udp"): raise ValueError(f"Invalid protocol: {protocol!r}")
        r = self._ufw("allow", f"{port}/{protocol}")
        return {"action": "allow_port", "port": port, "protocol": protocol, "success": r["returncode"] == 0}
    def deny_port(self, port: int, protocol: str = "tcp") -> Dict[str, Any]:
        if not (1 <= port <= 65535): raise ValueError(f"Invalid port: {port}")
        if protocol not in ("tcp", "udp"): raise ValueError(f"Invalid protocol: {protocol!r}")
        r = self._ufw("deny", f"{port}/{protocol}")
        return {"action": "deny_port", "port": port, "protocol": protocol, "success": r["returncode"] == 0}
    def get_status(self):
        r = self._ufw("status", "numbered")
        return {"ufw_output": r["stdout"], "blocked_ips": list(self._blocked_ips),
                "total_rules": len(self._rule_log)}
    def get_rule_log(self, limit: int = 50): return self._rule_log[-limit:]
