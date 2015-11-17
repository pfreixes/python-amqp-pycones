from flask import Flask

from task_queue_worker import expensive_task, fast_task


app = Flask(__name__)


@app.route('/expensive-task/<task_name>', methods=['POST'])
def execute_expensive_task(task_name):
    task_result = expensive_task.apply_async(args=[task_name])
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
    task_result = fast_task.apply_async(args=[task_name])
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
    app.run()
