"""Public service routes."""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from manager import HostingManager
from pricing import PricingEngine
from processor import DataProcessor

router = APIRouter()
hosting_manager = HostingManager()
pricing_engine = PricingEngine()
data_processor = DataProcessor()


class ProcessRequest(BaseModel):
    data: Any
    operation: str
    options: dict[str, Any] | None = Field(default=None)


@router.get("/hosting/plans")
async def get_hosting_plans(request: Request) -> dict[str, Any]:
    orchestrator = getattr(request.app.state.agent_manager, "agents", {}).get("orchestrator")
    if orchestrator:
        routed = await orchestrator.execute({"type": "list_plans"})
        if routed.get("status") == "routed":
            return routed["result"]
    return {"plans": hosting_manager.get_plans()}


@router.get("/hosting/ip-pricing")
async def get_hosting_ip_pricing(request: Request) -> dict[str, Any]:
    orchestrator = getattr(request.app.state.agent_manager, "agents", {}).get("orchestrator")
    if orchestrator:
        routed = await orchestrator.execute({"type": "list_ip_pricing"})
        if routed.get("status") == "routed":
            return routed["result"]
    return pricing_engine.get_ovhcloud_us_ip_pricing()


@router.get("/hosting/status")
async def get_hosting_status(request: Request) -> dict[str, Any]:
    orchestrator = getattr(request.app.state.agent_manager, "agents", {}).get("orchestrator")
    if orchestrator:
        routed = await orchestrator.execute({"type": "status", "target_agent": "devops"})
        if routed.get("status") == "routed":
            services_status = routed["result"].get("services", {})
            if services_status and services_status.get("status") == "operational":
                return services_status
    return hosting_manager.get_service_status()


@router.post("/data/process")
async def process_data(payload: ProcessRequest, request: Request) -> dict[str, Any]:
    result = await data_processor.process(payload.data, payload.operation, payload.options)
    analytics = getattr(request.app.state.agent_manager, "agents", {}).get("analytics")
    if analytics:
        await analytics.execute(
            {
                "type": "record_metric",
                "metric": "processed_requests",
                "value": 1.0,
            }
        )
    return result
