from app.tasks.celery_app import celery


@celery.tasks(name="periodic_task")
def periodic_task():
    print(12345)
