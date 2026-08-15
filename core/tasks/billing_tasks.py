"""Billing-related Celery tasks."""

from agents.monetization.agent import MonetizationAgent


def check_failed_payments() -> dict:
    return {"status": "simulated", "checked": True}


def detect_upsell_opportunities() -> dict:
    agent = MonetizationAgent()
    return {"opportunities": agent.client_manager.detect_upsell_opportunities()}
