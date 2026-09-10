"""Notification helpers exposed to agents."""

from agents.analytics.reporter import Reporter


class NotificationTools:
    """Facade for email/report notifications."""

    def __init__(self) -> None:
        self.reporter = Reporter()

    def daily_report(self, data: dict) -> dict:
        return self.reporter.generate_daily_report(data)


__all__ = ["NotificationTools"]
