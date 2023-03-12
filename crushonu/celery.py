import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crushonu.settings')

app = Celery('crushonu')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'backup_database': {
        'task': 'crushonu.apps.authentication.tasks.backup_database',
        'schedule': crontab(hour=0, minute=0),
    }
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
