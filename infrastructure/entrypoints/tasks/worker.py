from tasks.celery_app import celery_app

@celery_app.task(name="tasks.worker.test_task")
def test_task(name: str):
    return f"Hello {name}, Janus is working!"
