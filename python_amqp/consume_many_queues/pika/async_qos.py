# -*- coding: utf-8 -*-
"""
Consume Many Queues Pika Asyncronous implementation with QoS variability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import pika

from itertools import (
    takewhile,
    izip,
    cycle,
    product)

from python_amqp.consume_many_queues.pika.async import Consumer as BaseConsumer
from python_amqp.consume_many_queues.consume_many_queues_base import ConsumeManyQueuesBase
from python_amqp.consume_many_queues.consume_many_queues_base import EXCHANGE_NAME, QUEUE_NAME


class Consumer(BaseConsumer):
    """ We overrid just some stuff form the Consumer already implemented by the Pika
    Async to implement the prefetch variability"""
    def __init__(self, ioloop, id_, messages, end_consumers, prefetch):
        self._prefetch = prefetch
        BaseConsumer.__init__(self, ioloop, id_, messages, end_consumers)

    def on_channel_open(self, channel):
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._channel.basic_qos(prefetch_size=0, prefetch_count=self._prefetch, all_channels=True)
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        for queue in self._queue_names:
            self._channel.basic_consume(self.on_message, queue)

    def add_queue(self, queue_name):
        # we can not bind the queue still because the channel is not available
        self._queue_names.append(queue_name)

    def on_consumer_cancelled(self, method_frame):
        if self._channel:
            self._channel.close()

    def on_message(self, _, basic_deliver, properties, message):
        self._rx += 1
        if self._rx == (self._messages * len(self._queue_names)):
            self._channel.basic_ack(basic_deliver.delivery_tag, multiple=True)

            # we managed all the messages expected, just mark it
            # and ask if there is still other consumers to finish
            self._end_consumers[self._consumer_id] = True
            self._channel.close()
            self._connection.close()
            if all(self._end_consumers):
                self._ioloop.stop()
        elif self._rx % self._prefetch == 0:
            self._channel.basic_ack(basic_deliver.delivery_tag, multiple=True)

class AsyncQoS(ConsumeManyQueuesBase):
    """
    This Test implements the consuming of messages using the Asyncronous pattern. Running
    a constant amount of Amqp connections sharing the same ioloop.

    As a main difference than the Async implementation it parametrize the QoS value. Getting
    values from 2 till QUEUES / 2 

    The number of connections used will be always 8
    """
    NAME = "Pika_Async_QoS"
    DESCRIPTION = "Consume messages using N connections asyncronoysly with prefetching"

    def parameters(self):
        return [{'prefetch': prefetch} for prefetch in
                takewhile(lambda prefetch: prefetch  < self.queues/2,
                          map(lambda _: 2**_, xrange(2, self.queues)))]

    def setUp(self, prefetch=2, connections=32):
        """ Create all connections necessary to run the parametrized test. Each connection will stablish a
        will bind on a set of queues.
        """
        self._ioloop = pika.adapters.select_connection.IOLoop()

        # All consumers share the follwoing array, each time that ones consumer
        # has finished its work checks if the other ones have finished their work, the
        # last one will close the ioloop.
        self._consumers_finsihed = [False] * connections

        self._consumers = [Consumer(self._ioloop, i, self.messages, self._consumers_finsihed, prefetch)
                           for i in xrange(0, connections)]

        # it spreads the queues over the consumers until they run out.
        map(lambda cq: cq[0].add_queue(QUEUE_NAME.format(number=cq[1])),
            izip(cycle(self._consumers), xrange(0, self.queues)))

    def test(self, connections=32, prefetch=2):
        """ Start the ioloop, connecte all consumers and then consume all messaages """
        self._ioloop.start()

