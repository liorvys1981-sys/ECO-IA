"""Public service routes."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from manager import HostingManager
from processor import DataProcessor


router = APIRouter()
hosting_manager = HostingManager()
data_processor = DataProcessor()


class ProcessRequest(BaseModel):
    data: Any
    operation: str
    options: Optional[Dict[str, Any]] = Field(default=None)


@router.get("/hosting/plans")
async def get_hosting_plans(request: Request) -> Dict[str, Any]:
    monetization = getattr(request.app.state.agent_manager, "agents", {}).get("monetization")
    if monetization:
        return await monetization.execute({"type": "list_plans"})
    return {"plans": hosting_manager.get_plans()}


@router.get("/hosting/status")
async def get_hosting_status() -> Dict[str, Any]:
    return hosting_manager.get_service_status()


@router.post("/data/process")
async def process_data(payload: ProcessRequest) -> Dict[str, Any]:
    return await data_processor.process(payload.data, payload.operation, payload.options)
