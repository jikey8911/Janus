import os
from celery import Celery

# Configuración por defecto si no existen variables de entorno
# Configuración por defecto si no existen variables de entorno
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Fallback mechanism: If Redis URL is default localhost and likely not running, use filesystem
# This is a dev-only convenience for the user
import socket
def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

use_redis = is_port_open(6379)
if not use_redis:
    print("⚠️ Redis not detected. Using Filesystem as Celery Broker (Dev Mode).")
    # Ensure folders exist
    os.makedirs(".celery/results", exist_ok=True)
    os.makedirs(".celery/schedule", exist_ok=True)
    
    BROKER_URL = "filesystem://"
    BACKEND_URL = "db+sqlite:///celery_results.sqlite"
    
    celery_app = Celery(
        "janus_tasks",
        broker=BROKER_URL,
        backend=BACKEND_URL,
        include=["infrastructure.entrypoints.celery_tasks"]
    )
    celery_app.conf.update(
        broker_transport_options={
            'data_folder_in': '.celery',
            'data_folder_out': '.celery',
            'data_folder_processed': '.celery'
        },
        result_extended=True
    )
else:
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
    "quick-scan-every-5-minutes": {
        "task": "periodic_quick_scan_task",
        "schedule": 300.0,  # 5 minutos (1 Job, Score > 80)
    },
    "poll-upwork-every-minute": {
        "task": "poll_upwork_events_task",
        "schedule": 60.0,  # 60 segundos (HU 4.1)
    },
}
