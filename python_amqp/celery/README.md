Usage
=====

Run the worker(s) with:

        $ celery worker -A task_queue_<n>_worker -P <pool> -c <concurrency> -Q <queue>,<queue> -n <node hostname>

Run the HTTP server with:

        $ python task_queue_<n>_server.py

Run the HTTP client command with (check help with ``--help`` option:

        $ python task_queue_<n>_client.py [single|concurrent|mixed]


Discourse
=========

General approach: From the tutorial to a full-fledged AMQP architecture: tackling AMQP bottlenecks with Celery.

[1]

- **Single task, single worker, single process**. Nice and easy.

[2]

* **n tasks, single worker, single process**.
    * Queue contention. Consumer needs more throughput.
    * Easy solution, increase worker concurrency. 
        * prefork
        * threads
        * eventlet
        * gevent
    * prefork is the most stable option. Eventlet and gevent *usually* work. threads is highly experimental...
    * For fast tasks, reduce latency by increasing QoS (QoS = roundtrip/task)

[3]

* **n^2 tasks, single worker, n processes**.
    * At some point, your machine won't be able to process enough messages.
    * It's time to go distributed! Start a new worker node
    * Careful with the prefetch_count, or messages can get stuck waiting at the worker buffer!
    * Celery let configure prefetch_count with CELERYD_PREFETCH_MULTIPLIER
    * prefetch_count == CELERYD_PREFETCH_COUNT * concurrency-slots
    * Be aware of default behaviour of Celery about acks: early_ack, means task is acked just before starting, so a new task will be prefetched while the former is being processed. This is usually not a problem, and using ack_late has its drawbacks too.

[4]

* **n^2 slow tasks, m^2 fast tasks, n workers, n processes**.
    * Again queue contention. Fast tasks are left starved at the queue waiting for expensive tasks to finish.
    * Worker specialization
    * [5] CELERY_ROUTES to the resque: Queue per task, queue per worker

[6]

* ** y users(n^2 slow tasks, m^2 fast tasks), n workers, n processes**.
    * Same issue when multiple users come to play.
    * Users compiting for worker time.
    * Fair queueing: A queue for user/session, n queues for worker.
    * Dynamic queue consumption with `worker.control.add_consumer`

[7]

* **Celery protocol**
```
{
  'task': <task_name>,
  'id': <UUID of the task instance>,
  'args': [<arg1>, <arg2>],
  'kwargs': {<kwarg1>: <val>, <kwarg2>: <val>},
  '...'
}
```

TODO:

[8]

* **Gotcha's: The case of ETA tasks and revokes**
    * ETA tasks are kept in worker's memory, and prefetch_count is increased.
    * Revoked tasks ids are also kept in memory
    * Only when a task is about to be executed, it is matched against revoked tasks table
    * Careful when using revoke as a way to update ETA of task. Tasks will only be revoked when they
      are sheduled to execute.
    * This might not be a problem memory wise, but in case of worker restart the message churn can be dramatic.
