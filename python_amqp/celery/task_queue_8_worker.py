from time import sleep, time

from celery import Celery


app = Celery('tasks', backend='amqp://', broker='amqp://')

app.conf.update({
    'CELERY_TRACK_STARTED': True,
    'CELERYD_PREFETCH_MULTIPLIER': 1,
    'CELERY_ROUTES': {
        'tasks.expensive_task': {'queue': 'expensive'},
        'tasks.fast_task': {'queue': 'fast'},
    }
})

@app.task(name='tasks.expensive_task')
def expensive_task(task_n):
    start = time()
    while time() < start + 1:
        pass
    return 'Hello, World, expensive task {}!'.format(task_n)


@app.task(name='tasks.fast_task')
def fast_task(task_n):
    sleep(.005)
    return 'Hello, World, fast task {}!'.format(task_n)
