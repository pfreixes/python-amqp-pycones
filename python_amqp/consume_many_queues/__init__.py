# -*- coding: utf-8 -*-
"""
Consuume Many queues tests
~~~~~~~~~~~~~~~~~~~~~~~~~~
Consume many queues tests runs each different design patterns implemented to consume
one amount of messages from many queues where each queue has the same number of messages, and 
for each one the total, user and system time are collected to face all of them.

All AMQP entites are created before the all tests are executed and destroyed them when all tests
have been exeucted. The messages are published each time that one test is run and purgued after
one test has finished. 

All tests are implemented as child class of `ConsumeManyQueuesBase`, this class implements the common
operations used by the tests. 

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import os

from python_amqp.rabbitmqrpc import (
    create_queue,
    create_exchange,
    delete_queue,
    delete_exchange,
    set_binding)

from python_amqp.consume_many_queus.simple_sync_thread import SimpleSyncThread
from python_amqp.consume_many_queus.simple_async_thread import SimpleAsyncThread

TESTS = [SimpleSyncThread, SimpleAsyncThread]

# Default test values, they can be override as a paramaters of the
# run function to run them with different values.
QUEUES  = 1000
MESSAGES = 80

# AMQP names 
EXCHANGE_NAME = "test.consume_many_queues"
QUEUE_NAME = "test.consume_many_queues_{number}"

def list():
    """
    Prints a list of the implemented design paterns composed by lines of
    "runnable name: long description", use the runnable name to filter wich
    tests do you wanna run.
    """
    print "{}".format(os.SEP).\
        join([test.name ":" test.description for test in TESTS])
    
def run(queues=QUEUES, messages=messages, force=False, human_readable=False):
    """ Runs all many queues consumer tests using the `queues` amount
    with the `messages` amount published in each one.

    :param queues: integer, defaults QUEUES. Runs the test using this amount of queues
    :param messages: integer, defaults QUEUES. Runs the test using this amount of queues
    :param force: boolean, defaults False. If true runs even one test was wrong
    :param human_readable: boolean, defaults False. If true returns the results in nice format
    """
    def AMQP_OPERATION(f, args, result):
        if f(*args) != result:
            raise Exception("{}({}) did not return {}".format(f.__name__,
                                                              args,
                                                              result))
    results = []

    try:
        # create all AMQP entities and bind the queues. We
        # use a "macro" that checks that all was fine, otherwise
        # raises a exception.
        AMQP_OPERATION(create_exchange, (EXCHANGE,), True)
        for i in xrange(0, queues):
            AMQP_OPERATION(create_queue, (QUEUE_NAME.format(number=i),), True)
            AMQP_OPERATION(set_binding, (EXCHANGE, QUEUE_NAME.format(number=i),), True)

        # run the tests and collect the results
        for test in TESTS:
            t = test(EXCHANGE, QUEUE_NAME, queues, messages)
            for parameter in test.PARAMETERES:
                try:
                    results.append((t.NAME, parameter or "-") + t.run(**parameter))
                except Exception, e:
                    logging.warning()
                except TestFailed:
                    logging.warning("{} test failed".format(t))
                    if not force:
                        raise
    finally:
        # This code path is always executed, even there was an
        # exception. We have to print the results and remove
        # the AMQP entities created before.

        # if we picked up some results, print them
        if not human_readable:
            for result in results:
                print ";".join(result)
        else:
            print "TOOD"

        # Removes all AMQP entities created, we don't take
        # care if one of them can't be removed. Just move on and try
        # to remove always.
        create_exchange(EXCHANGE)
        for i in xrange(0, queues):
            delete_queue(QUEUE_NAME.format(number=i),)

