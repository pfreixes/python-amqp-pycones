# -*- coding: utf-8 -*-
"""
Consume Many Queues class
~~~~~~~~~~~~~~~~~~~~~~~~~

ManyConsumerTest publishes a class to be used by all tests that want be run in one
controlled enviornment, this is responsable to leave the queues ready to be consumed
by the consumers.

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import times
import logging
import traceback

from time import sleep

from python_amqp.publisher import Publisher
from python_amqp.rabbitmqrpc import (
    list_queues,
    purge_queue,
    info_queue)


# AMQP names
EXCHANGE_NAME = "test.consume_many_queues"
QUEUE_NAME = "test.consume_many_queues_{number}"


class TestFailed(Exception):
    """Adhoc exception to raise exceptional issuess because of Test didn't
    perform the task to consume all messages even it finished fine"""
    pass


class ConsumeManyQueuesBase(object):
    """ConsumeManyQueuesBase is the base class used by the specific tests that wants
    to consume a number of messages in a number of queues using different implementations
    """
    # Give a name and description
    NAME = None
    DESCRIPTION = None

    def __init__(self, exchange, queue_name, queues, messages):
        # Configuration of the test
        self.exchange = exchange
        self.queue_name = queue_name
        self.queues = queues
        self.messages = messages

    def __new__(cls, *args, **kwargs):
        """ Check that the child class implements the NAME, DESCRIPTION,
        and PARAMETERS attributes using the right types"""
        instance = object.__new__(cls, *args, **kwargs)

        for attr in ['NAME', 'DESCRIPTION']:
            if not getattr(instance, attr):
                raise ValueError("Attribute `{}` has to be declared".format(attr))

        return instance

    def run(self, *args,  **kwargs):
        """ Runs the test setting the environment publishing the amount of `messages` to
        all `queues` where each queue is composed by the `queue_name` format.
        """
        # publish the messagess to each queue, we use a fanout exchange
        # that has been bind for all queues. Each mesage that is published
        # is sent to all queues.
        publisher = Publisher()
        for i in xrange(0, self.messages):
            publisher.publish("message {}".format(i), self.exchange)

        # wait until all messages are ready to be consumed in
        # all queues. Even each iteration perfoms a RPC and has a
        # a implicit latence we add a sleep each time that fails
        # to avoid make to many requests.
        while not self._all_messages_published():
            sleep(0.1)

        try:
            t = times.Times()
            self.test(*args, **kwargs)
            real, user, sys = t.times()
        except Exception, e:
            # We purge the messages that are still there and
            # raise the exception got
            self._purge_messages()
            raise

        return real, user, sys

    def parameters(self, *args, **kwargs):
        """ If you want to run your test many times with different parameters, override
        this function and return a list of dictionaries. Each dictionary will be passed
        as keyword arguments of the test function.

        For example with the list [{'threads': 2}, {'threads': 4}], the test function
        will be called twice with threads 2 and 4.

        If this function is not override the test function will be called once without
        params
        """
        return [{}]

    def setUp(self, *args, **kwargs):
        """Before the test function being called this function will be called, the Test class
        can use this function to leave the environment ready. Use it to avoid compute none
        specific Test operation times such us create threads, etc.

        This function will be called with the same parameters with its analog test
        function.
        """
        pass  # by default do nothing

    def test(self, *args, **kwargs):
        """ Override this method with the test code """
        raise NotImplmented()

    def tearDown(self, *args, **kwargs):
        """ After the test function being called this function will be called, the Test class
        can use this function to leave the environment clean. Use it to avoid compute none
        specific Test operation times such us delete threads, etc.

        This function will be called with the same parameters with its analog test
        function,
        """
        pass  # by default do nothing

    def _purge_messages(self):
        """ Purge messages from queues if they stil exist, return the number of
        messages purged.
        """
        logging.debug('Queue purging after test finished')
        total = 0
        for i in xrange(0, self.queues):
            queue_name = self.queue_name.format(number=i)
            info = info_queue(queue_name)
            if info['messages'] > 0:
                logging.info('Queue {} has still {} messages'.format(queue_name, info['messages']))
                total = total + info['messages']
                purge_queue(queue_name)

        return total

    def _all_messages_published(self):
        """ Finds out if all messages are published, return True or False """
        messages = [info_queue(self.queue_name.format(number=i))['messages']
                    for i in xrange(0, self.queues)]
        return sum(messages) == (self.queues * self.messages)
