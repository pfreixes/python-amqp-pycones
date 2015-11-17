from uuid import uuid4
from time import sleep

import requests
import click


session_token = None

poll_freq_option = click.option('--poll-freq', '-p', default=1, show_default=True, type=float,
                                help='Seconds every which to poll the status of the tasks')

@click.group()
@click.pass_context
def main(ctx):
    global session_token
    session_token = login()
    ctx.call_on_close(logout)


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


@main.command(name='concurrent')
@click.argument('n', type=int, metavar='TASK_NUMBER')
@poll_freq_option
def n_concurrent_tasks(n, poll_freq):
    pending_tasks = {}
    for task_n in range(n):
        task_id = execute_expensive_task(task_n)
        print 'Started execution of task', task_n
        pending_tasks[task_n] = task_id
    while pending_tasks:
        for task_n, task_id in pending_tasks.items():
            status = get_expensive_task_status(task_id)
            print 'Task', task_n, 'status:', status
            if status == 'SUCCESS':
                result = get_expensive_task_result(task_id)
                print 'Task', task_n, 'result:', result
                del pending_tasks[task_n]
        sleep(poll_freq)


@main.command(name='mixed')
@click.argument('n_fast', type=int, metavar='FAST_TASK_NUMBER')
@click.argument('m_expensive', type=int, metavar='EXPENSIVE_TASK_NUMBER')
@poll_freq_option
def n_mixed_concurrent_tasks(n_fast, m_expensive, poll_freq):
    pending_fast_tasks = {}
    pending_expensive_tasks = {}
    for task_n in range(m_expensive):
        task_id = execute_expensive_task(task_n)
        print 'Started execution of expensive task', task_n
        pending_expensive_tasks[task_n] = task_id
    for task_n in range(n_fast):
        task_id = execute_fast_task(task_n)
        print 'Started execution of fast task', task_n
        pending_fast_tasks[task_n] = task_id
    while pending_fast_tasks or pending_expensive_tasks:
        for task_n, task_id in pending_fast_tasks.items():
            status = get_fast_task_status(task_id)
            print 'Fast task', task_n, 'status:', status
            if status == 'SUCCESS':
                result = get_fast_task_result(task_id)
                print 'Fast task', task_n, 'result:', result
                del pending_fast_tasks[task_n]
        for task_n, task_id in pending_expensive_tasks.items():
            status = get_expensive_task_status(task_id)
            print 'Expensive task', task_n, 'status:', status
            if status == 'SUCCESS':
                result = get_expensive_task_result(task_id)
                print 'Expensive task', task_n, 'result:', result
                del pending_expensive_tasks[task_n]
        sleep(poll_freq)



def login():
    return requests.post('http://localhost:5000/login').text

def logout():
    requests.post('http://localhost:5000/logout', headers={'Session-Token': session_token})

def execute_expensive_task(task_name):
    return requests.post('http://localhost:5000/expensive-task/{}'.format(task_name),
                         headers={'Session-Token': session_token}).text

def get_expensive_task_status(task_id):
    return requests.get('http://localhost:5000/expensive-task/{}/status'.format(task_id),
                        headers={'Session-Token': session_token}).text

def get_expensive_task_result(task_id):
    return requests.get('http://localhost:5000/expensive-task/{}'.format(task_id),
                        headers={'Session-Token': session_token}).text


def execute_fast_task(task_name):
    return requests.post('http://localhost:5000/fast-task/{}'.format(task_name),
                         headers={'Session-Token': session_token}).text

def get_fast_task_status(task_id):
    return requests.get('http://localhost:5000/fast-task/{}/status'.format(task_id),
                        headers={'Session-Token': session_token}).text

def get_fast_task_result(task_id):
    return requests.get('http://localhost:5000/fast-task/{}'.format(task_id),
                        headers={'Session-Token': session_token}).text


if __name__ == '__main__':
    main()


