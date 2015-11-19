from time import sleep

from celery import Celery
from pymongo import MongoClient


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
    sleep(5)
    MongoClient().foo.bar.update({'name': 'foo'}, {'$inc': {'bar': 1}}, upsert=True)
    return 'Hello, World, expensive task {}!'.format(task_n)


@app.task(name='tasks.fast_task')
def fast_task(task_n):
    sleep(.005)
    pymongo().foo.bar.update({'name': 'foo'}, {'$inc': {'bar': 1}}, upsert=True)
    return 'Hello, World, fast task {}!'.format(task_n)
