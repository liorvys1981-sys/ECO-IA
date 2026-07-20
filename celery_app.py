"""ECO-IA Celery application — distributed task queue."""

from celery import Celery
from celery.schedules import crontab

from settings import REDIS_URL

app = Celery(
    "eco_ia",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "core.tasks.backup_tasks",
        "core.tasks.health_tasks",
        "core.tasks.billing_tasks",
        "core.tasks.analytics_tasks",
    ],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
    beat_schedule={
        "hourly-backup": {
            "task": "core.tasks.backup_tasks.run_backup",
            "schedule": crontab(minute=0),
        },
        "health-check": {
            "task": "core.tasks.health_tasks.check_all_services",
            "schedule": 60.0,
        },
        "daily-report": {
            "task": "core.tasks.analytics_tasks.send_daily_report",
            "schedule": crontab(hour=8, minute=0),
        },
        "daily-cleanup": {
            "task": "core.tasks.health_tasks.cleanup_resources",
            "schedule": crontab(hour=0, minute=0),
        },
        "billing-check": {
            "task": "core.tasks.billing_tasks.check_failed_payments",
            "schedule": crontab(minute=30),
        },
        "upsell-check": {
            "task": "core.tasks.billing_tasks.detect_upsell_opportunities",
            "schedule": crontab(hour=9, minute=0),
        },
    },
)
