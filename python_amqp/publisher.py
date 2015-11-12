# -*- coding: utf-8 -*-
"""
Publisher in Pika
~~~~~~~~~~~~~~~~~~

Implements a publisher using the pika bloking drivers. Use it to publish messages.

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import pika

class Publisher(object):
    def __init__(self, host='localhost'):
        """ Intialize a AMQP connection and one channel to the `host` to be used by the publish method to publish
        messages through it.

        :param host: string, use one alternaltive host than the default one.
        """
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self._channel = self._connection.channel()

    def publish(self, message, exchange, routing_key=''):
        """ Send a message over the `exchange` using a `routing_key`.

        :param message: string, message by it self as string buffer. No codified.
        :param exchange: string, exchange name.
        :param routing_key: string, use a routing key for none fanout exchanges.
        """
        return self._channel.basic_publish(
            exchange,
            routing_key,
            message, 
            pika.BasicProperties(content_type='text/plain', delivery_mode=1)
        )

    def close(self):
        """ Is a good practice close the connection explicity. It gets sure that the messages
        still in the buffer are sent and doesn't leave the responsability to close the socket to 
        the GC when the object is deleted as a side effect of the destructor call"""
        self._channel.close()
        self._connection.close()
