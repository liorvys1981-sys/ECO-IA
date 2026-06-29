"""ECO-IA Celery application — distributed task queue."""

import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

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
        # Backups horarios
        "hourly-backup": {
            "task": "core.tasks.backup_tasks.run_backup",
            "schedule": crontab(minute=0),
        },
        # Health check cada minuto
        "health-check": {
            "task": "core.tasks.health_tasks.check_all_services",
            "schedule": 60.0,
        },
        # Reporte diario a las 8 UTC
        "daily-report": {
            "task": "core.tasks.analytics_tasks.send_daily_report",
            "schedule": crontab(hour=8, minute=0),
        },
        # Cleanup diario a medianoche
        "daily-cleanup": {
            "task": "core.tasks.health_tasks.cleanup_resources",
            "schedule": crontab(hour=0, minute=0),
        },
        # Billing check cada hora
        "billing-check": {
            "task": "core.tasks.billing_tasks.check_failed_payments",
            "schedule": crontab(minute=30),
        },
        # Upsell check diario
        "upsell-check": {
            "task": "core.tasks.billing_tasks.detect_upsell_opportunities",
            "schedule": crontab(hour=9, minute=0),
        },
    },
)
