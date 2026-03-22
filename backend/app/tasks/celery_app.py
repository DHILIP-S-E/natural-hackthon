"""AURA Celery App — Background task processing with Redis broker."""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "aura",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "refresh-climate-every-6h": {
            "task": "app.tasks.climate_tasks.refresh_all_cities_climate",
            "schedule": crontab(minute=0, hour="*/6"),
        },
        "send-booking-reminders-hourly": {
            "task": "app.tasks.notification_tasks.send_booking_reminders",
            "schedule": crontab(minute=0),
        },
        "calculate-attrition-weekly": {
            "task": "app.tasks.staff_tasks.calculate_attrition_risk",
            "schedule": crontab(minute=0, hour=2, day_of_week=1),  # Monday 2am
        },
    },
)

# Auto-discover tasks in all task modules
celery_app.autodiscover_tasks(["app.tasks"])
