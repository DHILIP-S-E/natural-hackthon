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
        # ── Existing ──
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
            "schedule": crontab(minute=0, hour=2, day_of_week=1),  # Monday 2am IST
        },
        # ── Feature 12: AuraPOINTS Loyalty ──
        "birthday-reminders-daily": {
            "task": "app.tasks.loyalty_tasks.send_birthday_reminders",
            "schedule": crontab(minute=0, hour=9),  # 9:00 AM IST
        },
        "tier-upgrade-check-daily": {
            "task": "app.tasks.loyalty_tasks.check_tier_upgrades",
            "schedule": crontab(minute=0, hour=0),  # Midnight IST
        },
        "re-engagement-daily": {
            "task": "app.tasks.loyalty_tasks.send_re_engagement",
            "schedule": crontab(minute=0, hour=10),  # 10:00 AM IST
        },
        # ── Feature 13: Post-Visit Homecare ──
        "post-checkout-homecare-15min": {
            "task": "app.tasks.homecare_tasks.send_post_checkout_homecare",
            "schedule": crontab(minute="*/15"),  # Every 15 min → catches 30-min window
        },
        "day7-rebooking-nudge-daily": {
            "task": "app.tasks.homecare_tasks.send_day7_rebooking_nudge",
            "schedule": crontab(minute=0, hour=11),  # 11:00 AM IST
        },
        # ── Feature 9: Inventory Forecasting ──
        "low-stock-check-daily": {
            "task": "app.tasks.inventory_tasks.check_low_stock",
            "schedule": crontab(minute=0, hour=7),  # 7:00 AM IST
        },
        "festival-demand-alerts-weekly": {
            "task": "app.tasks.inventory_tasks.send_festival_demand_alerts",
            "schedule": crontab(minute=0, hour=8, day_of_week=0),  # Sunday 8:00 AM IST
        },
        # ── Feature 14: Eco Tracker ──
        "green-salon-badge-monthly": {
            "task": "app.tasks.eco_tasks.calculate_monthly_green_salon_badge",
            "schedule": crontab(minute=0, hour=6, day_of_month=1),  # 1st of month 6 AM IST
        },
        # ── Feature 16: AuraScore ──
        "aurascore-weekly-anomaly-scan": {
            "task": "app.tasks.aurascore_tasks.weekly_score_anomaly_scan",
            "schedule": crontab(minute=0, hour=6, day_of_week=1),  # Monday 6 AM IST
        },
        # ── Feature 18: Franchise Dashboard — weekly revenue anomaly check ──
        "franchise-revenue-anomaly-weekly": {
            "task": "app.tasks.franchise_tasks.check_revenue_anomalies",
            "schedule": crontab(minute=30, hour=6, day_of_week=1),  # Monday 6:30 AM IST
        },
    },
)

# Auto-discover tasks in all task modules
celery_app.autodiscover_tasks(["app.tasks"])
