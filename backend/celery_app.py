"""
celery_app.py
-------------
Celery application factory using SQLite as the broker and backend.
Works on Windows without Redis/WSL.

Start worker (from project root):
    celery -A backend.celery_app:celery_app worker --loglevel=info --pool=solo

Start beat scheduler (from project root):
    celery -A backend.celery_app:celery_app beat --loglevel=info
"""

from celery import Celery
from celery.schedules import crontab
import os

# SQLite broker + result backend paths (relative to project root)
_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_INSTANCE = os.path.join(_BASE, 'instance')
os.makedirs(_INSTANCE, exist_ok=True)

BROKER_URL = f"sqla+sqlite:///{_INSTANCE}/celery_broker.db"
RESULT_URL = f"db+sqlite:///{_INSTANCE}/celery_results.db"

celery_app = Celery(
    "placement_portal",
    broker=BROKER_URL,
    backend=RESULT_URL,
    include=["backend.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    result_expires=3600,
    # ── Beat schedule ──────────────────────────────────────────────
    beat_schedule={
        # Interview reminders: every day at 8:00 AM IST
        "daily-interview-reminders": {
            "task": "backend.tasks.send_interview_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
        # Monthly placement report: 1st of each month at 7:00 AM IST
        "monthly-placement-report": {
            "task": "backend.tasks.generate_monthly_placement_report",
            "schedule": crontab(hour=7, minute=0, day_of_month=1),
        },
    },
)
