from celery import Celery

celery = Celery('tasks', broker='amqp://', backend='amqp://')


celery.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='Europe/Oslo',
    CELERY_TRACK_STARTED = True
)


@celery.task(name='tasks.add')
def add(x, y):
    return x + y
