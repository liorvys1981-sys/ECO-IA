"""Webhook endpoints for ECO-IA."""

import json

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request):
    try:
        payload = json.loads(await request.body())
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    event_type = payload.get("type")
    if event_type == "invoice.payment_succeeded":
        invoice = payload.get("data", {}).get("object", {})
        return {
            "status": "ok",
            "action": "payment_recorded",
            "invoice_id": invoice.get("id"),
        }

    return {"status": "ignored", "event_type": event_type}
