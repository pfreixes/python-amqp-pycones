# -*- coding: utf-8 -*-
"""
Consume Many Queues class
~~~~~~~~~~~~~~~~~~~~~~~~~

ManyConsumerTest publishes class to be used by all tests that wants be run in one
controlled enviornment, this is responsable to leave the queues ready to be consumed
by the consuumers run by the child class.

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import os

from python_amqp.rabbitmqrpc import (
    list_queues,
    purge_queue)

class ConsumeManyQueuesBase(object):
    """ConsumeManyQueuesBase is the base class used by the specific tests that wants
    to consume a number of messages in a number of queues using different implementations
    """
    # Give a name and description
    NAME  = None
    DESCRIPTION = None

    # override this field if you want to run your test with different
    # configgurations, by default jus one NO configuration is given
    PARAMETERS = [{}]

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

        for attr in ['NAME', 'DESCRPTION']:
            if not getattr(instance, attr):
                raise ValueError("Attribute `{}` has to be declared".format(attr))

        if not isinstance(instance.PARAMETERS, list):
            raise ValueError("Attribute `PARAMETERS` has to be a lsit")

        return instance

    def run(self, *args,  **kw):
        """ Runs the test setting the environment publishing the amount of `messages` to
        all `queues` where each queue is composed by the `queue_name` format.
        """
        # publish the messagess to each queue, we use a fanout exchange
        # that has been bind with all queues. Each mesage that is published 
        # is sent to all queues
        publisher = Publisher()
        for i in xrange(0, messages):
           pubiisher.publish("message {}".format(i), exchange)

        # wait until all messages are ready to be consumed in 
        # all queues. Even each iteration perfoms a RPC and has a 
        # a implicit latence we add a sleep each time that fails
        # to avoid make to many requests.
        while not self._all_messge_published():
           sleep(0.1)

        try:
            t = timer()
            self.test(*args, **kwargs)
            total, user, sys = t.stop()
        except Exception, e:
            # We purge the messages that are still there and
            # raise the exception got
            self._purge_messages()
            raise    
        finally:
            if self._purge_messages() > 0:
                # The test finisheded ok but there are still
                # messages published, this is a error. We
                # raise the properly error
                raise TestFalied()
       
        return total, user, sys 
        
    def test(self, *args, **kwargs):
        """ Override this method with the test code """
        raise NotImplmented()

    test = None
