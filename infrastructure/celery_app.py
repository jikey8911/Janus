import os
from celery import Celery

# Configuración por defecto si no existen variables de entorno
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "janus_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["infrastructure.entrypoints.celery_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Configuración para tareas periódicas (Celery Beat)
celery_app.conf.beat_schedule = {
    "scan-jobs-every-10-minutes": {
        "task": "scan_jobs_task",
        "schedule": 600.0,  # 10 minutos
    },
}
