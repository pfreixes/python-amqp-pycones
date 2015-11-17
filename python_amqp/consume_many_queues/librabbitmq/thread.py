# -*- coding: utf-8 -*-
"""
Consume Many Queues Librabbitmq Threading implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import threading
import librabbitmq

from itertools import takewhile, izip, cycle

from python_amqp.consume_many_queues.consume_many_queues_base import ConsumeManyQueuesBase
from python_amqp.consume_many_queues.consume_many_queues_base import EXCHANGE_NAME, QUEUE_NAME


class Consumer(threading.Thread):
    def __init__(self, *args, **kwargs):
        self._rx = 0
        self._queues = 0
        self._finished = False
        self._messages = kwargs.pop("messages")
        self._connection = librabbitmq.Connection()
        self._channel = self._connection.channel()
        self._channel.basic_qos(prefetch_count=1)
        threading.Thread.__init__(self, *args, **kwargs)

    def add_queue(self, queue):
        # bind the queue
        self._channel.basic_consume(queue, callback=self._callback, )
        self._queues += 1

    def _callback(self, message):
        message.ack()
        self._rx += 1
        # the amount of messages that this consumer should get
        # is the total amount of messages of the all queues bind.
        if self._rx == (self._messages * self._queues):
            self._finished = True
            self._connection.close()

    def run(self):
        try:
            while True:
                self._connection.drain_events()
        except librabbitmq.ConnectionError:
            # when we drain events over connection that
            # has already closed a ConnectionError is
            # raised, just take care that it was made
            # in a control way
            if not self._finished:
                raise


class Thread(ConsumeManyQueuesBase):
    """
    This Test implements the consuming of messages using the Threading pattern. Each
    thread instance holds a LibRabbitmq connection bind over a set of queues.

    The amount of threads are parametrized with a grow factor of ^2 from 2 till the
    first number greater than the number of queues divided by 2.

    For example, for a 100 queues. Test executed are with 2, 4, 8, 16, 32 and 64
    threads.

    Queues are distributed between the different consumers with proportionally,
    however when the number of queues and the number of threads are not divisibles
    by them self, the amount of queues by each thread will not the same.
    """
    NAME = "Librabbitmq_Threads"
    DESCRIPTION = "Each Thread runs a librabbitmq connection consuming mulitple queues"

    def parameters(self):
        return [{"threads": threads} for threads in
                takewhile(lambda threads: threads < self.queues/2,
                          map(lambda _: 2**_, xrange(1, self.queues)))]

    def setUp(self, threads=2):
        """ Create all threads necessary to run the parametrized test. Each thread will stablish a
        connection and will bind on a set of queues.
        """
        self._threads = [Consumer(messages=self.messages) for i in xrange(0, threads)]

        # it spreads the queues over the consumers until they run out.
        map(lambda tq: tq[0].add_queue(QUEUE_NAME.format(number=tq[1])),
            izip(cycle(self._threads), xrange(0, self.queues)))

    def test(self, threads=2):
        """ Start the treads to consume all messaages """
        map(lambda thread: thread.start(), self._threads)
        return map(lambda thread: thread.join(), self._threads)
