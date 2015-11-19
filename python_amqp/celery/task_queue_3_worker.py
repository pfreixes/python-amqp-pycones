from time import sleep

from celery import Celery


app = Celery('tasks', backend='amqp://', broker='amqp://')

app.conf.update({
    'CELERY_TRACK_STARTED': True,
    'CELERYD_PREFETCH_MULTIPLIER': 1,
})

@app.task(name='tasks.expensive_task')
def expensive_task(task_n):
    sleep(5)
    return 'Hello, World, expensive task {}!'.format(task_n)
