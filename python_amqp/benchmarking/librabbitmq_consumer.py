from time import sleep
from multiprocessing.pool import ThreadPool
from threading import Thread

import librabbitmq

QUEUE = 'demo_durable'


def single_consumer_single_channel_single_connection_qos_one_quick_task():
    def consume(message):
        # 5ms task
        # sleep(0.005)
        message.ack()
    connection = librabbitmq.Connection()
    channel = connection.channel()
    channel.basic_qos(prefetch_count=2000000)
    channel.basic_consume(QUEUE, callback=consume)
    while True:
        connection.drain_events()


def two_consumer_two_queues_single_channel_single_connection_qos_one_quick_task():
    def consume(message):
        # 5ms task
        # sleep(0.005)
        message.ack()
    connection = librabbitmq.Connection()
    channel = connection.channel()
    channel.basic_qos(prefetch_count=2000000)
    for x in range(10):
        channel.basic_consume(QUEUE + str(x), callback=consume)
    while True:
        connection.drain_events()


def single_consumer_single_channel_n_threads_single_connection_qos_one_quick_task(n):
    def consume(message):
        # 5ms task
        sleep(0.005)
        message.ack()  # AMQP is not Thread-Safe in the channel level!!
    connection = librabbitmq.Connection()
    thread_pool = ThreadPool(n)
    channel = connection.channel()
    channel.basic_qos(prefetch_count=2)
    channel.basic_consume(QUEUE, callback=lambda message: thread_pool.apply_async(consume, [message]))
    while True:
        connection.drain_events()


def n_consumer_n_channels_n_threads_single_connection_qos_one_quick_task(n):
    def setup_thread(channel):
        def consume(message):
            # 5ms task
            sleep(0.005)
            message.ack()
        channel.basic_qos(prefetch_count=2)
        # Here each message.ack is done on a different channel
        channel.basic_consume(QUEUE, callback=consume)
    connection = librabbitmq.Connection()
    for consumer in range(n):
        channel = connection.channel()
        # Connections in librabbitmq are not Thread-Safe! Cannot use the maxim
        # "Channel-per-thread", only "Connection-per-thread". This code explodes
        thread = Thread(target=setup_thread, args=[channel])
        thread.daemon = True
        thread.start()

    while True:
        connection.drain_events()


def single_consumer_single_channel_n_threads_n_connections_qos_one_quick_task(n):
    def drain_threaded(connection):
        while True:
            connection.drain_events()
    def consume(message):
        # 5ms task
        sleep(0.005)
        message.ack()
    for x in range(n):
        connection = librabbitmq.Connection()
        channel = connection.channel()
        channel.basic_qos(prefetch_count=2)
        # Here each message.ack is done on a different channel
        channel.basic_consume(QUEUE, callback=consume)
        thread = Thread(target=drain_threaded, args=[connection])
        thread.start()


def single_consumer_single_channel_n_threads_n_connections_n_queues_qos_one_quick_task(n):
    def drain_threaded(connection):
        while True:
            connection.drain_events()
    def consume(message):
        # 5ms task
        # sleep(0.005)
        message.ack()
    for x in range(n):
        connection = librabbitmq.Connection()
        channel = connection.channel()
        channel.queue_declare(QUEUE+str(x), durable=True)
        channel.queue_bind(QUEUE+str(x), exchange='demo_fanout' + str(x))
        channel.basic_qos(prefetch_count=200000000)
        # Here each message.ack is done on a different channel
        channel.basic_consume(QUEUE+str(x), callback=consume)
        thread = Thread(target=drain_threaded, args=[connection])
        thread.start()

# single_consumer_single_channel_single_connection_qos_one_quick_task()
# two_consumer_two_queues_single_channel_single_connection_qos_one_quick_task()
# single_consumer_single_channel_n_threads_single_connection_qos_one_quick_task(2)
# n_consumer_n_channels_n_threads_single_connection_qos_one_quick_task(2)
# single_consumer_single_channel_n_threads_n_connections_qos_one_quick_task(50)
single_consumer_single_channel_n_threads_n_connections_n_queues_qos_one_quick_task(100)
