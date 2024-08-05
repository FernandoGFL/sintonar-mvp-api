import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sintonar.settings')

app = Celery('sintonar')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'backup_database': {
        'task': 'sintonar.apps.authentication.tasks.backup_database',
        'schedule': crontab(hour=0, minute=0),
    }
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
