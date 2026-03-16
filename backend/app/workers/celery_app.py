from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "visor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
    beat_schedule={
        # Sync Open Finance a cada 30 minutos
        "sync-open-finance": {
            "task": "app.workers.tasks.sync_all_tenants",
            "schedule": 1800.0,
        },
    },
)
