from celery import Celery, Task
from flask import Flask
from celery.schedules import crontab
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class CeleryConfig():
    broker_url = 'redis://localhost:6379/0'
    result_backend = 'redis://localhost:6379/1'
    timezone = 'Asia/Kolkata'
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    broker_connection_retry_on_startup = True
    beat_schedule = {
        # Run daily at 6 PM
        'send-daily-reminders': {
            'task': 'backend.celery.tasks.send_pending_request_reminders',
            'schedule': crontab(hour=18, minute=0),
        },
        # Run on the 1st day of every month at midnight
        'send-monthly-activity-report': {
            'task': 'backend.celery.tasks.send_monthly_activity_report',
            'schedule': crontab(day_of_month=1, hour=0, minute=0),
        },
    }

class FlaskTask(Task):
    flask_app = None
    def __call__(self, *args: object, **kwargs: object) -> object:
        with self.flask_app.app_context():
            return self.run(*args, **kwargs)

def celery_init_app(app: Flask) -> Celery:
    FlaskTask.flask_app = app
    
    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(CeleryConfig)
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    with app.app_context():
        import backend.celery.celery_schedule
    
    return celery_app