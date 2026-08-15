"""Analytics-related Celery tasks."""

from agents.analytics.dashboard import DashboardData
from agents.analytics.reporter import Reporter


def send_daily_report() -> dict:
    dashboard = DashboardData()
    reporter = Reporter()
    snapshot = dashboard.snapshot()
    report = reporter.generate_daily_report(snapshot)
    return {"status": "generated", "report": report}
