# -*- coding: utf-8 -*-
"""
Consume Many Queues Pika Asyncronous implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import pika

from itertools import takewhile, izip, cycle

from python_amqp.consume_many_queues.consume_many_queues_base import ConsumeManyQueuesBase
from python_amqp.consume_many_queues.consume_many_queues_base import EXCHANGE_NAME, QUEUE_NAME


class Consumer(object):
    def __init__(self, ioloop, id_, messages, end_consumers):
        self._consumer_id = id_
        self._messages = messages
        self._queue_names = []
        self._rx = 0
        self._ioloop = ioloop
        self._end_consumers = end_consumers
        self._connection = None
        self._channel = None
        self._closing = False
        self._connection = pika.SelectConnection(
            pika.ConnectionParameters(host='localhost', socket_timeout=1000),
            self.on_connection_open,
            custom_ioloop=self._ioloop,
            stop_ioloop_on_close=False)

    def close_connection(self):
        self._connection.close()

    def on_connection_closed(self, connection, reply_code, reply_text):
        pass

    def on_connection_open(self, unused_connection):
        self._connection.add_on_close_callback(self.on_connection_closed)
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_closed(self, channel, reply_code, reply_text):
        self._connection.close()

    def on_channel_open(self, channel):
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._channel.basic_qos(prefetch_size=0, prefetch_count=1, all_channels=True)
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
        self._channel.basic_ack(basic_deliver.delivery_tag)
        self._rx += 1
        if self._rx == (self._messages * len(self._queue_names)):
            # we managed all the messages expected, just mark it
            # and ask if there is still other consumers to finish
            self._end_consumers[self._consumer_id] = True
            self._channel.close()
            self._connection.close()
            if all(self._end_consumers):
                self._ioloop.stop()

    def on_cancelok(self, unused_frame):
        self._channel.close()

    def stop_consuming(self):
        if self._channel:
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def stop(self):
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()


class Async(ConsumeManyQueuesBase):
    """
    This Test implements the consuming of messages using the Asyncronous pattern. Running
    a specific amount of Amqp connections sharing the same ioloop.

    The amount of conections are parametrized with a grow factor of ^2, from 2 till the
    first number greater than the number of queues divided by 2.

    For example, for a 100 queues. Test executed are with 2, 4, 8, 16, 32 and 64
    connections.

    Queues are distributed between the different connections with proportionally,
    however when the number of queues and the number of threads are not divisibles
    by them self, the amount of queues by each connection will not the same.

    Because of the architecture of the test the connection time take by each consumer
    is also computed aside of the time used to consume the messages by them self. It can
    decrease a bit the metrics of this implementation.
    """
    NAME = "Pika_Async"
    DESCRIPTION = "Consume messages using N connections sharing the same ioloop"

    def parameters(self):
        return [{"connections": connections} for connections in
                takewhile(lambda connections: connections < self.queues/2,
                          map(lambda _: 2**_, xrange(1, self.queues)))]

    def setUp(self, connections=2):
        """ Create all connections necessary to run the parametrized test. Each connection will stablish a
        will bind on a set of queues.
        """
        self._ioloop = pika.adapters.select_connection.IOLoop()

        # All consumers share the follwoing array, each time that ones consumer
        # has finished its work checks if the other ones have finished their work, the
        # last one will close the ioloop.
        self._consumers_finsihed = [False] * connections

        self._consumers = [Consumer(self._ioloop, i, self.messages, self._consumers_finsihed)
                           for i in xrange(0, connections)]

        # it spreads the queues over the consumers until they run out.
        map(lambda cq: cq[0].add_queue(QUEUE_NAME.format(number=cq[1])),
            izip(cycle(self._consumers), xrange(0, self.queues)))

    def test(self, connections=2):
        """ Start the ioloop, connecte all consumers and then consume all messaages """
        self._ioloop.start()

