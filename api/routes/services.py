"""Service endpoints for ECO-IA."""

from fastapi import APIRouter
from pydantic import BaseModel

from pricing import PricingEngine

router = APIRouter()
pricing_engine = PricingEngine()


class DataProcessRequest(BaseModel):
    data: dict
    operation: str


@router.get("/hosting/plans")
async def hosting_plans():
    return {"plans": pricing_engine.list_plans()}


@router.get("/hosting/status")
async def hosting_status():
    return {"status": "operational"}


@router.post("/data/process")
async def data_process(payload: DataProcessRequest):
    return {
        "status": "processed",
        "operation": payload.operation,
        "data": payload.data,
    }
