from time import sleep

from celery import Celery


app = Celery('tasks', backend='amqp://', broker='amqp://')

app.conf.update({
    'CELERY_TRACK_STARTED': True,
    'CELERY_TASK_SERIALIZER': 'json',
    'CELERY_RESULT_SERIALIZER': 'json',
    'CELERYD_PREFETCH_MULTIPLIER': 1,
    'CELERY_QUEUES': {
        'expensive': {'exchange': 'main-exchange',
                                 'exchange_type': 'topic',
                                 'routing_key': 'tasks.expensive_task'},
        'fast': {
                            'exchange': 'main-exchange',
                            'exchange_type': 'topic',
                            'routing_key': 'tasks.fast_task'},
    }
})

@app.task(name='tasks.expensive_task')
def expensive_task(task_n):
    sleep(5)
    return 'Hello, World, expensive task {}!'.format(task_n)


@app.task(name='tasks.fast_task')
def fast_task(task_n):
    sleep(.005)
    return 'Hello, World, fast task {}!'.format(task_n)
