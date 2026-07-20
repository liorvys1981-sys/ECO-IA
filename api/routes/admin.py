"""Admin endpoints for ECO-IA."""

import os

from fastapi import APIRouter, Header, HTTPException

from optimizer import ResourceOptimizer

router = APIRouter()

_AGENTS = [
    {"name": "orchestrator", "description": "Master coordinator", "status": "active"},
    {"name": "monetization", "description": "Pricing and billing", "status": "active"},
    {"name": "devops", "description": "Deployments and healing", "status": "active"},
    {"name": "resources", "description": "Resource optimisation", "status": "active"},
    {"name": "security", "description": "Firewall and audit", "status": "active"},
    {"name": "analytics", "description": "Reporting and prediction", "status": "active"},
]

_SCHEDULER_TASKS = [
    {"task_id": "health_check", "description": "Ping all agents", "interval_seconds": 60},
    {"task_id": "executive_report", "description": "Generate executive report", "interval_seconds": 3600},
]


def _validate_admin_key(admin_key: str | None):
    expected_key = os.getenv("ECO_IA_ADMIN_KEY", "")
    if not expected_key or admin_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid or missing admin key")


@router.get("/health")
async def admin_health(x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")):
    _validate_admin_key(x_admin_key)
    return {"status": "healthy", "agents": _AGENTS}


@router.get("/metrics")
async def admin_metrics(x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")):
    _validate_admin_key(x_admin_key)
    return ResourceOptimizer().get_metrics()


@router.get("/agents")
async def list_agents(x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")):
    _validate_admin_key(x_admin_key)
    return {"agents": _AGENTS, "total": len(_AGENTS)}


@router.get("/scheduler/tasks")
async def scheduler_tasks(x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")):
    _validate_admin_key(x_admin_key)
    return {"tasks": _SCHEDULER_TASKS}
