# -*- coding: utf-8 -*-
"""
Consume Many Queues TxAmqp Asyncronous implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import os

from twisted.internet import reactor
from txamqp_ext.factory import AmqpReconnectingFactory
from twisted.internet.defer import inlineCallbacks, returnValue

from itertools import takewhile, izip, cycle

from python_amqp.consume_many_queues.consume_many_queues_base import ConsumeManyQueuesBase
from python_amqp.consume_many_queues.consume_many_queues_base import EXCHANGE_NAME, QUEUE_NAME


class Consumer(object):
    def __init__(self, id_, messages, end_consumers):
        self._consumer_id = id_
        self._messages = messages
        self._queue_names = []
        self._rx = 0
        self._end_consumers = end_consumers
        self._connection = None
        self._channel = None
        self._closing = False

        # sepecific options for the txamqp factory constructor
        kwargs = {
            'host': 'localhost',
            'port': 5672,
            'user': 'guest',
            'password': 'guest',
            'spec': os.path.join(os.path.dirname(__file__), 'amqp0-9-1.xml'),
            'prefetch_count': 1,
            'skip_decoding': True
        }
        self._client = AmqpReconnectingFactory(self, **kwargs)

    def add_queue(self, queue_name):
        self._queue_names.append(queue_name)
        self._client.setup_read_queue(
            EXCHANGE_NAME,
            routing_key='unused',
            callback=self.on_message,
            queue_name=queue_name,
            autodeclare=False)

    def on_message(self, msg):
        # ack is made by the txamqp_ext by it self after proccess the message
        self._rx += 1
        if self._rx == (self._messages * len(self._queue_names)):
            self._end_consumers[self._consumer_id] = True
            if all(self._end_consumers):
                reactor.stop()

class Async(ConsumeManyQueuesBase):
    """
    This Test implements the consuming of messages using the Asyncronous pattern with
    Twisted.

    Current implementation only suports binding one queue per connection, it means
    that this test is parametrize always with the connections = QUEUES.
    """
    NAME = "Twisted_Async"
    DESCRIPTION = "Consume messages using N connections"

    def parameters(self):
        # Current implementation of TXAMQP only suports one queue binding per
        # consumer/connection.
        return [{"connections": self.queues}]

    def setUp(self, connections=2):
        """ Create all connections necessary to run the parametrized test. Each connection will stablish a
        will bind on a set of queues.
        """
        # All consumers share the follwoing array, each time that ones consumer
        # has finished its work checks if the other ones have finished their work, the
        # last one will close the ioloop.
        self._consumers_finsihed = [False] * connections

        self._consumers = [Consumer(i, self.messages, self._consumers_finsihed)
                           for i in xrange(0, connections)]

        # it spreads the queues over the consumers until they run out.
        map(lambda cq: cq[0].add_queue(QUEUE_NAME.format(number=cq[1])),
            izip(cycle(self._consumers), xrange(0, self.queues)))

    def test(self, connections=2):
        """ Start the reactor, connect all consumers and then consume all messaages """
        reactor.run()

