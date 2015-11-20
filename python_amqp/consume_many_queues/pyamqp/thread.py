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


class Consumer(threading.Thread):
    def __init__(self, *args, **kwargs):
        self._rx = 0
        self._messages = kwargs.pop("messages")
        self._queue_name = None
        self._connection = amqp.Connection()
        self._channel = self._connection.channel()
        threading.Thread.__init__(self, *args, **kwargs)

    def add_queue(self, queue):
        self._queue_name = queue

    def run(self):
        class StopConsuming(Exception):
            pass
        def consume(message):
            message.channel.basic_ack(delivery_tag=message.delivery_tag)
            self._rx += 1
            if self._rx == self._messages:
                raise StopConsuming()

        self._channel.basic_consume(self._queue_name, callback=consume)
        while True:
            try:
                self._connection.drain_events()
            except StopConsuming:
                return  # exit


class Thread(ConsumeManyQueuesBase):
    """
    This Test implements the consuming of messages using the Threading pattern with
    thE pyamqp driver. Each thread instance holds a connection and each connection
    binds to one queue.

    Because pyamqp doesn't allow to consume from several queues using just one
    Consumer this test is not parametrized and always run the number of connections
    as the number of queues configured.
    """
    NAME = "Pyamqp_Threads"
    DESCRIPTION = "Each Thread runs a Pyamqp bloking adpater"

    def parameters(self):
        return [{'connections': self.queues}]

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
