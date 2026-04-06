try:
    from .celery import app as celery_app
except ModuleNotFoundError as exc:
    # Allow Django to boot even when Celery is not installed locally.
    if exc.name != "celery":
        raise
    celery_app = None

__all__ = ("celery_app",)
