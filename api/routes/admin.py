"""Admin routes."""

from fastapi import APIRouter, Request

from agents.resources.optimizer import ResourceOptimizer

router = APIRouter()
optimizer = ResourceOptimizer()


@router.get("/health")
async def admin_health(request: Request) -> dict:
    manager = request.app.state.agent_manager
    return {
        "status": "healthy",
        "agents": [agent["name"] for agent in manager.list_agents()["agents"]],
    }


@router.get("/metrics")
async def admin_metrics() -> dict:
    return optimizer.get_metrics()


@router.get("/agents")
async def admin_agents(request: Request) -> dict:
    return request.app.state.agent_manager.list_agents()


@router.get("/scheduler/tasks")
async def scheduler_tasks(request: Request) -> dict:
    orchestrator = request.app.state.agent_manager.agents["orchestrator"]
    return {"tasks": orchestrator.scheduler.list_tasks()}
