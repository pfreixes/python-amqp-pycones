# -*- coding: utf-8 -*-
"""
Consume Many Queues Pika Threading implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import pika
import threading

from python_amqp.consume_many_queues.consume_many_queues_base import ConsumeManyQueuesBase


class Consumer(threading.Thread):
    def __init__(self, *args, **kwargs):
        self._rx = 0
        self._queues = 0
        self._messages = kwargs.pop("messages")
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
        self._channel = self._connection.channel()
        self._channel.basic_qos(prefetch_size=0, prefetch_count=1, all_channels=True)
        threading.Thread.__init__(self, *args, **kwargs)

    def add_queue(self, queue):
        # bind the queue
        self._channel.basic_consume(self._callback, queue=queue)
        self._queues += 1

    def _callback(self, channel, method, properties, message):
        self._channel.basic_ack(delivery_tag=method.delivery_tag)
        self._rx += 1

        # the amount of messages that this consumer should get
        # is the total amount of messages of the all queues
        # bind.
        if self._rx == (self._messages * self._queues):
            # when the stop consuming is called it stops the loop
            # and the run function is terminated and the thread
            self.channel.stop_consuming()

    def run(self):
        self.channel.start_consuming()


class Thread(ConsumeManyQueuesBase):
    """
    This Test implements the consuming of messages using the Threading pattern. Each
    thread instance holds a Blocking Pika adapter bind over a set of queues.

    The amount of threads are parametrized with a grow factor of ^2 from 2 till the
    first number greater than the number of queues divided by 2.

    For example, for a 100 queues. Test executed are with 2, 4, 8, 16, 32 and 64
    threads.

    Queues are distributed between the different consumers with proportionally,
    however when the number of queues and the number of threads are not divisibles
    by them self, the amount of queues by each thread will not the same.
    """
    NAME = "Pika Threads"
    DESCRIPTION = "Each Thread runs a Pika bloking adpater, threads"

    def parameters(self):
        return [{"threads": threads} for threads in
                takewhile(lambda threads: threads < self.queues/2,
                          map(lambda _: 2**_, xrange(1, self.queues)))]

    def setUp(self, threads=2):
        """ Create all threads necessary to run the parametrized test. Each thread will stablish a
        connection and will bind on a set of queues.
        """
        self._threads = [Consumer(messages=self.messages, number=i) for i in xrange(0, threads)]

        # it spreads the queues over the consumers until they run out.
        map(lambda thread, queue: thread.bind_queue(self.queue.format(queue)),
            izip(cycle(self._threads), xrange(0, self.queues)))

    def test(self, threads=2):
        """ Start the treads to consume all messaages """
        map(lambda thread: thread.start(), self._threads)
        return map(lambda thread: thread.join(), self._threads)
