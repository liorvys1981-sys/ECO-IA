"""Analytics-related Celery tasks."""

import asyncio

from agents.analytics.agent import AnalyticsAgent


def send_daily_report() -> dict:
    agent = AnalyticsAgent()
    snapshot = asyncio.run(agent.execute({"type": "snapshot"}))
    report = asyncio.run(agent.execute({"type": "daily_report", "data": snapshot}))
    return {"status": "generated", "report": report}
