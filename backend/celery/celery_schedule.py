from celery.schedules import crontab
from flask import current_app as app
from backend.celery.tasks import email_reminder, send_pending_request_reminders

celery_app = app.extensions['celery']




