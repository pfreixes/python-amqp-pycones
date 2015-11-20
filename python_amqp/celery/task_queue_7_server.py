import json
from uuid import uuid4

import rabbitpy
from flask import Flask

from task_queue_7_worker import expensive_task, fast_task


app = Flask(__name__)


@app.route('/expensive-task/<task_name>', methods=['POST'])
def execute_expensive_task(task_name):
    task_id = schedule_task('expensive_task', args=[task_name])
    return task_id

@app.route('/expensive-task/<task_id>/status', methods=['GET'])
def get_status_expensive_task(task_id):
    return get_task_status('expensive_task', task_id)

@app.route('/expensive-task/<task_id>', methods=['GET'])
def get_expensive_task(task_id):
    return get_task_result('expensive_task', task_id)


@app.route('/fast-task/<task_name>', methods=['POST'])
def execute_fast_task(task_name):
    task_id = schedule_task('fast_task', args=[task_name])
    return task_id

@app.route('/fast-task/<task_id>/status', methods=['GET'])
def get_status_fast_task(task_id):
    return get_task_status('fast_task', task_id)

@app.route('/fast-task/<task_id>', methods=['GET'])
def get_fast_task(task_id):
    return get_task_result('fast_task', task_id)


def schedule_task(task_name, args=None, kwargs=None):
    args = args or []
    kwargs = kwargs or {}
    task_id = str(uuid4())
    protocol = {
        'task': 'tasks.{}'.format(task_name),
        'id': task_id,
        'args': args,
        'kwargs': kwargs
    }
    rabbitpy.simple.publish(
        exchange_name='main-exchange',
        routing_key='tasks.{}'.format(task_name),
        body=json.dumps(protocol),
        properties={'content_type': 'application/json'}
    )
    return task_id

def get_task_status(task_name, task_id):
    queue_name = task_id.replace('-', '')
    with rabbitpy.connection.Connection() as conn:
        with conn.channel() as channel:
            status = 'PENDING'
            while True:
                message = rabbitpy.amqp_queue.Queue(channel, queue_name).get()
                if message is None:
                    break
                else:
                    status = message.json()['status']
    return status

def get_task_result(task_name, task_id):
    queue_name = task_id.replace('-', '')
    for message in rabbitpy.simple.consume(queue_name=queue_name):
        if message.json()['status'] != 'SUCCESS':
            continue
        return message.json()['result']


if __name__ == '__main__':
    app.run(debug=True)
