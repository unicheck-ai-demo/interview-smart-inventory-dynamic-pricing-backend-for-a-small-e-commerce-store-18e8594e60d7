"""Celery application configuration."""

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Handy task to verify that Celery is wired correctly."""
    request_id = getattr(self.request, 'id', 'unknown')
    print(f'Celery debug task executed. Request id: {request_id}')


__all__ = ('app',)
