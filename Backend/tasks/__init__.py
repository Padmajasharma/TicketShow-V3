# backend/tasks/__init__.py
from extensions import celery
from .emails import send_email_reminder, send_booking_confirmation
from .reports import generate_monthly_report


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        2000.0,
        send_email_reminder.s(),
        name="send_email_reminder_to_all_users",
    )
    sender.add_periodic_task(
        60.0,
        generate_monthly_report.s(),
        name="generate_monthly_report",
    )
