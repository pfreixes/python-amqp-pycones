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

All tests are implemented as child class of `ConsumeManyQueuesBase`, this class implements the
common operations used by the tests.

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import os
import logging

from python_amqp.rabbitmqrpc import (
    create_queue,
    create_exchange,
    delete_queue,
    delete_exchange,
    set_binding)

from python_amqp.consume_many_queues.pika import Thread as PikaThread
from python_amqp.consume_many_queues.pika import Async as PikaAsync

TESTS = [PikaThread, PikaAsync]

# Default test values, they can be override as a paramaters of the
# run function to run them with different values.
QUEUES = 1000
MESSAGES = 80

# AMQP names
EXCHANGE_NAME = "test.consume_many_queues"
QUEUE_NAME = "test.consume_many_queues_{number}"


def list():
    """
    Prints a list of the implemented tests paterns composed by lines of
    "test name: short description", use the test name to filter wich
    tests do you wanna run or get more info.
    """
    print "{}".format(os.SEP).\
        join([test.NAME + ":" + test.DESCRIPTION for test in TESTS])


def info(test_name):
    """
    Returns the whole info of a test
    """
    test = filter(lambda t: t.name == test_name, TESTS)
    if not test:
        print "Test {} have not found".format(test_name)
    else:
        print test.__doc__


def run(queues=QUEUES, messages=MESSAGES):
    """ Runs all many queues consumer tests using the `queues` amount
    with the `messages` amount published in each one.

    :param queues: integer, defaults QUEUES. Runs the test using this amount of queues
    :param messages: integer, defaults MESSAGES. Runs the test using this amount of messages
    :param force: boolean, defaults False. If true runs even one test was wrong
    :param human_readable: boolean, defaults False. If true returns the results in nice format
    """
    logging.info("Running tests")

    def AMQP_OPERATION(f, args, result):
        if f(*args) != result:
            raise Exception("{}({}) did not return {}".format(f.__name__,
                                                              args,
                                                              result))
    try:
        # create all AMQP entities and bind the queues. We
        # use a "macro" that checks that all was fine, otherwise
        # raises a exception.
        logging.debug("Creating the Exchange {}".format(EXCHANGE))
        AMQP_OPERATION(create_exchange, (EXCHANGE,), True)
        for i in xrange(0, queues):
            queue_name = QUEUE_NAME.format(number=i)
            logging.debug("Creating the Queue {} and binding it".format(queue_name))
            AMQP_OPERATION(create_queue, (queue_name,), True)
            AMQP_OPERATION(set_binding, (EXCHANGE, queue_name,), True)

        # run the tests and collect the results
        for test in TESTS:
            t = test(EXCHANGE, QUEUE_NAME, queues, messages)
            for parameters in test.parameters():
                logging.info("{} running with params {}".format(test.NAME, parameters))
                try:
                    t.setUp(**parameters)
                    print "Real {}s, User {}s, Sys {}s".format(*t.run(**parameters))
                except (Exception, TestFailed), e:
                    logging.warning("{} failed {}".format(test.NAME, str(e)))
                    logging.debug(traceback.format_exc())
                finally:
                    # always call the tearDown method for the specific
                    # test to avoid leave the environment dirty.
                    try:
                        t.tearDown(**parameters)
                    except Exception:
                        logging.warning("{} tearDown failed".format(test.NAME))
    finally:
        # We have to remove the AMQP entities created before
        # event there was a exception.
        delete_exchange(EXCHANGE)
        for i in xrange(0, queues):
            delete_queue(QUEUE_NAME.format(number=i))
