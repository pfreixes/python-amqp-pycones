# -*- coding: utf-8 -*-
"""
Consume Many Queues Pika Asyncronous implementation with QoS variability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
        self._prefetch = kwargs.pop("prefetch")
        self._queues = 0
        self._connection = amqp.Connection()
        self._channel = self._connection.channel()
        self._channel.basic_qos(0, self._prefetch, True)
        threading.Thread.__init__(self, *args, **kwargs)

    def add_queue(self, queue):
        self._channel.basic_consume(queue, callback=self._callback)
        self._queues += 1

    def _callback(self, message):
        self._rx += 1
        if self._rx == (self._messages * self._queues):
            message.channel.basic_ack(delivery_tag=message.delivery_tag, multiple=True)
            self._channel.close()
            self._connection.close()
            raise StopConsuming()
        elif self._rx % self._prefetch == 0:
            message.channel.basic_ack(delivery_tag=message.delivery_tag, multiple=True)

    def run(self):
        while True:
            try:
                self._connection.drain_events()
            except StopConsuming:
                return  # exit


class ThreadQoS(ConsumeManyQueuesBase):
    """
    This Test implements the consuming of messages using the Threading pattern with
    the pyamqp driver. Each thread instance holds connections and each connection
    binds to a set of queues.

    As a main difference than the Thread implementation it parametrize the QoS value. Getting
    values from 2 till QUEUES / 2 

    The number of connections used will be always 16
    """
    NAME = "Pyamqp_Threads_QoS"
    DESCRIPTION = "Consume messages using N connections with prefetching"

    def parameters(self):
        return [{'prefetch': prefetch} for prefetch in
                takewhile(lambda prefetch: prefetch  < self.queues/2,
                          map(lambda _: 2**_, xrange(2, self.queues)))]

    def setUp(self, prefetch=2, connections=32):
        """ Create all threads necessary to run the parametrized test. Each thread will stablish a
        connection and will bind to one queues.
        """
        self._threads = [Consumer(prefetch=prefetch, messages=self.messages) for i in xrange(0, connections)]

        map(lambda tq: tq[0].add_queue(QUEUE_NAME.format(number=tq[1])),
            izip(cycle(self._threads), xrange(0, self.queues)))

    def test(self, prefetch=2, connections=32):
        """ Start the treads to consume all messaages """
        map(lambda thread: thread.start(), self._threads)
        return map(lambda thread: thread.join(), self._threads)
