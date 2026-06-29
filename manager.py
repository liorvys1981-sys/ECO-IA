"""Hosting service manager — manages hosted environments."""
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

HOSTING_PLANS = {
    "basic": {
        "name": "Basic",
        "price_usd": 9.99,
        "cpu_cores": 0.5,
        "ram_gb": 0.5,
        "storage_gb": 10,
        "bandwidth_gb": 100,
        "max_instances": 1,
        "uptime_sla": 99.0,
    },
    "pro": {
        "name": "Pro",
        "price_usd": 49.99,
        "cpu_cores": 2,
        "ram_gb": 2,
        "storage_gb": 100,
        "bandwidth_gb": 1000,
        "max_instances": 5,
        "uptime_sla": 99.9,
    },
    "enterprise": {
        "name": "Enterprise",
        "price_usd": 199.99,
        "cpu_cores": 8,
        "ram_gb": 16,
        "storage_gb": 1000,
        "bandwidth_gb": 10000,
        "max_instances": 20,
        "uptime_sla": 99.99,
    },
}


class HostingManager:
    """Manages hosted service instances for clients."""

    def __init__(self):
        self._instances: Dict[str, Dict[str, Any]] = {}
        self._server_ip = os.getenv("SERVER_IP", "135.148.232.10")

    def get_plans(self) -> List[Dict[str, Any]]:
        """Return all available hosting plans."""
        return [{"plan_key": k, **v} for k, v in HOSTING_PLANS.items()]

    def get_plan(self, plan_key: str) -> Optional[Dict[str, Any]]:
        return HOSTING_PLANS.get(plan_key)

    def provision_instance(self, client_id: str, plan: str) -> Dict[str, Any]:
        """Provision a hosting instance for a client."""
        plan_config = HOSTING_PLANS.get(plan)
        if not plan_config:
            return {"status": "error", "message": f"Unknown plan: {plan}"}
        instance_id = f"eco-{client_id[:8]}"
        instance = {
            "instance_id": instance_id,
            "client_id": client_id,
            "plan": plan,
            "status": "running",
            "server_ip": self._server_ip,
            "created_at": datetime.utcnow().isoformat(),
            "resources": plan_config,
        }
        self._instances[instance_id] = instance
        logger.info("Provisioned instance %s for client %s (plan: %s)",
                    instance_id, client_id, plan)
        return instance

    def get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        return self._instances.get(instance_id)

    def list_instances(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        instances = list(self._instances.values())
        if client_id:
            instances = [i for i in instances if i["client_id"] == client_id]
        return instances

    def get_service_status(self) -> Dict[str, Any]:
        return {
            "status": "operational",
            "server": self._server_ip,
            "uptime_pct": 99.9,
            "active_instances": len([i for i in self._instances.values() if i["status"] == "running"]),
            "timestamp": datetime.utcnow().isoformat(),
        }
