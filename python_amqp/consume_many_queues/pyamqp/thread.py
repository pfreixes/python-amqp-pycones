# -*- coding: utf-8 -*-
"""
Consume Many Queues Rabbitpy  implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import amqp
import threading

from itertools import takewhile, izip, cycle

from python_amqp.consume_many_queues.consume_many_queues_base import ConsumeManyQueuesBase
from python_amqp.consume_many_queues.consume_many_queues_base import EXCHANGE_NAME, QUEUE_NAME


class StopConsuming(Exception):
    pass

class Consumer(threading.Thread):
    def __init__(self, *args, **kwargs):
        self._rx = 0
        self._messages = kwargs.pop("messages")
        self._queues = 0
        self._connection = amqp.Connection()
        self._channel = self._connection.channel()
        threading.Thread.__init__(self, *args, **kwargs)

    def add_queue(self, queue):
        self._channel.basic_consume(queue, callback=self._callback)
        self._queues += 1

    def _callback(self, message):
        message.channel.basic_ack(delivery_tag=message.delivery_tag)
        self._rx += 1
        if self._rx == (self._messages * self._queues):
            self._channel.close()
            self._connection.close()
            raise StopConsuming()

    def run(self):
        while True:
            try:
                self._connection.drain_events()
            except StopConsuming:
                return  # exit


class Thread(ConsumeManyQueuesBase):
    """
    This Test implements the consuming of messages using the Threading pattern with
    thE pyamqp driver. Each thread instance one connections and each connection
    binds to a set of queues.

    The amount of threads are parametrized with a grow factor of ^2 from 2 till the
    first number greater than the number of queues divided by 2.

    For example, for a 100 queues. Test executed are with 2, 4, 8, 16, 32 and 64
    threads.
    """
    NAME = "Pyamqp_Threads"
    DESCRIPTION = "Each Thread runs a Pyamqp bloking adpater"

    def parameters(self):
        return [{"connections": threads} for threads in
                takewhile(lambda threads: threads < self.queues/2,
                          map(lambda _: 2**_, xrange(1, self.queues)))]

    def setUp(self, connections=2):
        """ Create all threads necessary to run the parametrized test. Each thread will stablish a
        connection and will bind to one queues.
        """
        self._threads = [Consumer(messages=self.messages) for i in xrange(0, connections)]

        map(lambda tq: tq[0].add_queue(QUEUE_NAME.format(number=tq[1])),
            izip(cycle(self._threads), xrange(0, self.queues)))

    def test(self, connections=2):
        """ Start the treads to consume all messaages """
        map(lambda thread: thread.start(), self._threads)
        return map(lambda thread: thread.join(), self._threads)
