from uuid import uuid4
from time import sleep

import requests
import click


poll_freq_option = click.option('--poll-freq', '-p',
                                default=1, show_default=True, type=float,
                                help="Seconds between polls of task's status")


@click.group()
def main():
    pass

@main.command(name='single')
@poll_freq_option
def single_task(poll_freq):
    task_id = execute_expensive_task('single')
    print 'Started execution of task', task_id
    status = None
    while status != 'SUCCESS':
        status = get_expensive_task_status(task_id)
        print 'Task status:', status
        sleep(poll_freq)
    result = get_expensive_task_result(task_id)
    print 'Task result:', result


def execute_expensive_task(task_name):
    uri = 'http://localhost:5000/expensive-task/{}'.format(task_name))
    return requests.post(uri).text

def get_expensive_task_status(task_id):
    uri = 'http://localhost:5000/expensive-task/{}/status'.format(task_id)
    return requests.get(uri).text

def get_expensive_task_result(task_id):
    uri = 'http://localhost:5000/expensive-task/{}'.format(task_id)
    return requests.get(uri).text


if __name__ == '__main__':
    main()
