web: uvicorn infrastructure.entrypoints.webhooks:app --host 0.0.0.0 --port $PORT
worker: celery -A infrastructure.celery_app worker --loglevel=info
