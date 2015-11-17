from time import sleep
from multiprocessing.pool import ThreadPool
from threading import Thread

import rabbitpy

QUEUE = 'demo_durable'


def single_consumer_single_channel_single_connection_qos_one_quick_task():
    with rabbitpy.Connection() as connection:
        with connection.channel() as channel:
            channel.prefetch_count(100000)
            for message in rabbitpy.Queue(channel, name=QUEUE):
                # sleep(0.005)
                message.ack()


def single_consumer_single_channel_n_threads_single_connection_qos_one_quick_task(n):
    def consume(message):
        # 5ms task
        sleep(0.005)
        message.ack()

    thread_pool = ThreadPool(n)
    with rabbitpy.Connection() as connection:
        with connection.channel() as channel:
            channel.prefetch_count(2)
            for message in rabbitpy.Queue(channel, name=QUEUE):
                thread_pool.apply_async(consume, [message])


def n_consumer_n_channels_n_threads_single_connection_qos_one_quick_task(n):
    def setup_thread(channel):
        def consume(message):
            # 5ms task
            sleep(0.005)
            message.ack()
        for message in rabbitpy.Queue(channel, name=QUEUE):
            consume(message)
    connection = rabbitpy.Connection()
    for consumer in range(n):
        channel = connection.channel()
        channel.prefetch_count(200)
        thread = Thread(target=setup_thread, args=[channel])
        thread.start()


def single_consumer_single_channel_n_threads_n_connections_qos_one_quick_task(n):
    def setup_connection():
        def consume(message):
            # 5ms task
            sleep(0.005)
            message.ack()
        connection = rabbitpy.Connection()
        channel = connection.channel()
        channel.prefetch_count(200)
        for message in rabbitpy.Queue(channel, name=QUEUE):
            consume(message)
    for x in range(n):
        thread = Thread(target=setup_connection)
        thread.start()


single_consumer_single_channel_single_connection_qos_one_quick_task()
# single_consumer_single_channel_n_threads_single_connection_qos_one_quick_task(100)
# n_consumer_n_channels_n_threads_single_connection_qos_one_quick_task(30)
# single_consumer_single_channel_n_threads_n_connections_qos_one_quick_task(30)
