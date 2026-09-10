"""Billing-related Celery tasks."""

import asyncio

from agents.monetization.agent import MonetizationAgent


def check_failed_payments() -> dict:
    agent = MonetizationAgent()
    return asyncio.run(agent.execute({"type": "check_failed_payments"}))


def detect_upsell_opportunities() -> dict:
    agent = MonetizationAgent()
    return asyncio.run(agent.execute({"type": "detect_upsell_opportunities"}))
