from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("green_power")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "aggregate-grid-rt-data-minutely": {
        "task": "apps.telemetry.tasks.aggregate_rt_data_minutely",
        "schedule": crontab(minute="*"),
    },
    "aggregate-grid-rt-data-ten-minutes": {
        "task": "apps.telemetry.tasks.aggregate_rt_data_ten_minutes",
        "schedule": crontab(minute="*/10"),
    },
    "aggregate-grid-rt-data-thirty-minutes": {
        "task": "apps.telemetry.tasks.aggregate_rt_data_thirty_minutes",
        "schedule": crontab(minute="*/30"),
    },
    "aggregate-grid-rt-data-three-hours": {
        "task": "apps.telemetry.tasks.aggregate_rt_data_three_hours",
        "schedule": crontab(minute=0, hour="*/3"),
    },
    "aggregate-grid-rt-data-six-hours": {
        "task": "apps.telemetry.tasks.aggregate_rt_data_six_hours",
        "schedule": crontab(minute=0, hour="*/6"),
    },
}
