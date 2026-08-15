"""Webhook endpoints."""

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse


router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    try:
        event = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON payload"})

    event_type = event.get("type", "")
    if event_type == "invoice.payment_succeeded":
        return {"status": "processed", "action": "payment_recorded"}
    if event_type == "invoice.payment_failed":
        return {"status": "processed", "action": "payment_failed"}
    return {"status": "ignored", "event_type": event_type}
