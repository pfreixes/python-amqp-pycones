# -*- coding: utf-8 -*-
"""
Asyncronous Consuemr Pika
~~~~~~~~~~~~~~~~~~~~~~~~~

Implements a interface to build asyncronous consumers with Pika. Queues to be bind
are given as constuctor param and messges are handled overriding the on_message function.

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import pika

from functools import partial


class ConsumerAsync(object):
    def __init__(self, queues, ioloop=None, qos=1, host='localhost'):
        """ Intialize a AMQP asyncronous connsumer bind to all queues given

        :param queues: list, list of queue names such as ['queue 1', 'queue 2']
        :param ioloop: pika.adapters.select_connection.IOLoop,
                       use an external loop insted the default one
        :param qos: integer, use another quality of service
        :param host: string, use one alternaltive host than default one
        """

        if not queues or isinstance(queues, list):
           raise ValueError("queues parameter list exepected and at least with one queue name")

        self._queues = queues

        # intialize default values
        self._qos = qos
        self._ioloop = ioloop
        self._host = host
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None

        # open the connection 
        self._connection = self.connect()

    def connect(self):
        return pika.SelectConnection(pika.ConnectionParameters(host=self._host, socket_timeout=1000),
                                     self.on_connection_open,
                                     custom_ioloop=self._ioloop,
                                     stop_ioloop_on_close=False if self._ioloop else True)

    def close_connection(self):
        self._connection.close()

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        self._connection.ioloop.stop()

    def on_connection_open(self, unused_connection):
        self._connection.add_on_close_callback(self.on_connection_closed)
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_closed(self, channel, reply_code, reply_text):
        self._connection.close()

    def on_channel_open(self, channel):
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._channel.basic_qos(prefetch_size=0, prefetch_count=self._qos, all_channels=True)
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        for queue in self._queues:
            on_message_with_queue = partial(self.on_message, queue)
            self._consumer_tags.append(self._channel.basic_consume(on_message_with_queue, queue)

    def on_consumer_cancelled(self, method_frame):
        if self._channel:
            self._channel.close()

    def on_message(self, queue_name,  channel, basic_deliver, properties, message):
        """ Override this function with your derivated class. Otherwise a NotImplemented
        exception is raise.

        :param queue_name: string, queue where this message comes from.
        :param channel: a
        :param basic_delivery: a
        :param properties:
        :param message:
        """
        raise NotImplemented()

    def on_cancelok(self, unused_frame):
        self._channel.close()

    def stop_consuming(self):
        if self._channel:
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def stop(self):
        self._closing = True
        self.stop_consuming()
