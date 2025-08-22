# celery_app/celery.py
import os
from celery import Celery
from celery.schedules import crontab

from datetime import datetime
import pytz




# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create Celery instance
app = Celery('arabic_sports_trends')

# Load configuration from Django settings with CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Explicitly set broker and backend (as a fallback)
app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Configure Celery Beat schedule to run daily at 12:01 AM UTC
app.conf.beat_schedule = {
    'run-full-pipeline-daily-at-midnight': {
        'task': 'celery_app.tasks.run_full_pipeline',
        'schedule': crontab(minute=0, hour=0),  # midnight UTC
    },
   
}

# Optional: Add Celery configuration overrides
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',  # Adjust if needed
    enable_utc=True,
)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    now_utc = datetime.now(pytz.UTC)
    print(f"Task triggered at UTC time: {now_utc}")  
    """Debug task to print request info."""
    print(f'Request: {self.request!r}')