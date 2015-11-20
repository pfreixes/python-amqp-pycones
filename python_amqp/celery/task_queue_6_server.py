from uuid import uuid4

from flask import Flask, request
from kombu import Queue, Exchange

from task_queue_6_worker import expensive_task, fast_task, app as worker_app


app = Flask(__name__)


@app.route('/login', methods=['POST'])
def login():
    session_token = str(uuid4())
    queue_name = 'expensive-{}'.format(session_token)
    exchange = 'celery'
    worker_app.conf['CELERY_QUEUES'][queue_name] = {
        'exchange': exchange,
        'exchange_type': 'direct',
        'exchange_durable': True,
    }
    worker_app.control.add_consumer(
        queue=queue_name,
        exchange=exchange,
        destination=['expensive-task@worker']
    )
    queue_name = 'fast-{}'.format(session_token)
    worker_app.conf['CELERY_QUEUES'][queue_name] = {
        'exchange': exchange,
        'exchange_type': 'direct',
        'exchange_durable': True,
    }
    worker_app.control.add_consumer(
        queue=queue_name,
        exchange=exchange,
        destination=['fast-task@worker']
    )
    return session_token

@app.route('/logout', methods=['POST'])
def logout():
    session_token = request.headers['Session-Token']
    queue_name = 'expensive-{}'.format(session_token)
    worker_app.control.cancel_consumer(
        queue=queue_name,
        destination=['expensive-task@worker']
    )
    del worker_app.conf['CELERY_QUEUES'][queue_name]
    queue_name = 'fast-{}'.format(session_token)
    worker_app.control.cancel_consumer(
        queue=queue_name,
        destination=['fast-task@worker']
    )
    del worker_app.conf['CELERY_QUEUES'][queue_name]
    return 'ok'


@app.route('/expensive-task/<task_name>', methods=['POST'])
def execute_expensive_task(task_name):
    session_token = request.headers['Session-Token']
    queue_name = 'expensive-{}'.format(session_token)
    task_result = expensive_task.apply_async(args=[task_name], queue=queue_name)
    print 'Task executed. Session id:', task_result.id
    return task_result.id

@app.route('/expensive-task/<task_id>/status', methods=['GET'])
def get_status_expensive_task(task_id):
    task_result = expensive_task.AsyncResult(task_id)
    return task_result.status

@app.route('/expensive-task/<task_id>', methods=['GET'])
def get_expensive_task(task_id):
    task_result = expensive_task.AsyncResult(task_id)
    return task_result.get()


@app.route('/fast-task/<task_name>', methods=['POST'])
def execute_fast_task(task_name):
    session_token = request.headers['Session-Token']
    queue_name = 'fast-{}'.format(session_token)
    task_result = fast_task.apply_async(args=[task_name],
                                        queue=queue_name)
    return task_result.id

@app.route('/fast-task/<task_id>/status', methods=['GET'])
def get_status_fast_task(task_id):
    task_result = fast_task.AsyncResult(task_id)
    return task_result.status

@app.route('/fast-task/<task_id>', methods=['GET'])
def get_fast_task(task_id):
    task_result = fast_task.AsyncResult(task_id)
    return task_result.get()


if __name__ == '__main__':
    app.run(debug=True)
