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

# Redis broker + result backend (Mandated for grading criteria)
BROKER_URL = "redis://localhost:6379/1"
RESULT_URL = "redis://localhost:6379/2"

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
