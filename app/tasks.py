"""Example Celery tasks for the project."""

from celery import shared_task


@shared_task(name='app.ping')
def ping() -> str:
    """Simple task used for health checks."""
    return 'pong'
