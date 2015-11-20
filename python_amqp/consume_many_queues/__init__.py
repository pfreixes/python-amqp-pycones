# -*- coding: utf-8 -*-
"""
Consume Many queues tests
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
from time import sleep

import os
import logging
import traceback

from python_amqp.rabbitmqrpc import (
    create_queue,
    create_exchange,
    delete_queue,
    delete_exchange,
    purge_queue,
    set_binding)

from python_amqp.consume_many_queues.pika import Async as PikaAsync
from python_amqp.consume_many_queues.pika import Thread as PikaThread
from python_amqp.consume_many_queues.pika import AsyncQoS as PikaAsyncQoS
from python_amqp.consume_many_queues.twisted import Async as TwistedAsync
from python_amqp.consume_many_queues.pyamqp import Thread as PyamqpThread
from python_amqp.consume_many_queues.pyamqp import ThreadQoS as PyamqpThreadQoS
from python_amqp.consume_many_queues.rabbitpy import Thread as RabbitpyThread
from python_amqp.consume_many_queues.librabbitmq import Thread as LibRabbitmqThread

from python_amqp.consume_many_queues.consume_many_queues_base import TestFailed
from python_amqp.consume_many_queues.consume_many_queues_base import EXCHANGE_NAME, QUEUE_NAME

def _installed_tests():
    return [
        PikaThread, PikaAsync, PikaAsyncQoS,
        TwistedAsync, RabbitpyThread, PyamqpThread,
        LibRabbitmqThread, PyamqpThreadQoS
    ]

def _red_message(message):
    # Used to print a message over the console using
    # the red color. Usefull to notice that one test failed
    return "\033[1;31m" + message + "\033[0m"


def _green_message(message):
    # Used to print a message over the console using
    # the green color. Usefull to notice that one test was fine.
    return "\033[1;32m" + message + "\033[0m"

# Default test values, they can be override as a paramaters of the
# run function to run them with different values.
QUEUES = 200
MESSAGES = 50

def list():
    """
    Returns the list of names and descriptions of implemented tests.
    """
    return [test.NAME + ": " + test.DESCRIPTION for test in _installed_tests()]


def info(test_name):
    """
    Returns the docstring of a test, or a string error if it is not found.
    """
    test = filter(lambda t: t.NAME == test_name, _installed_tests())
    if not test:
        return "Test {} have not found".format(test_name)
    else:
        return test[0].__doc__


def run(tests=None, queues=None, messages=None):
    """ Runs all many queues consumer tests using the `queues` amount
    with the `messages` amount published in each one.

    The tests to be executed can be filtered using the *args, setting as
    arguments those test that we wanna run.

    :param tests: list, Runs only these tests i.e ['pika_thread', ['pika_async']
                               By default runs all tests
    :param queues: integer, defaults QUEUES. Runs the test using this amount of queues
    :param messages: integer, defaults MESSAGES. Runs the test using this amount of messages
    """
    def AMQP_OPERATION(f, args, result):
        if f(*args) != result:
            raise Exception("{}({}) did not return {}".format(f.__name__,
                                                              args,
                                                              result))

    queues_ = queues if queues else QUEUES
    messages_ = messages if messages else MESSAGES
    tests_ = tests

    logging.info('Running the tests with {} messages and {} queues, total messages {}'.format(messages_,
                                                                                              queues_,
                                                                                              messages_*queues_))

    try:
        # create all AMQP entities and bind the queues. We
        # use a "macro" that checks that all was fine, otherwise
        # raises a exception.
        logging.info("Creating the Exchange {}".format(EXCHANGE_NAME))
        AMQP_OPERATION(create_exchange, (EXCHANGE_NAME, 'fanout'), True)
        logging.info("Creating {} queues".format(queues_))
        for i in xrange(0, queues_):
            queue_name = QUEUE_NAME.format(number=i)
            logging.debug("Creating the Queue {} and binding it".format(queue_name))
            AMQP_OPERATION(create_queue, (queue_name,), True)
            AMQP_OPERATION(purge_queue, (queue_name,), True)
            AMQP_OPERATION(set_binding, (EXCHANGE_NAME, queue_name, 'queue'), True)

        logging.info("Queues created")
        logging.info("Running tests")
        results = []
        for test in _installed_tests():

            logging.info("+ {} test".format(test.NAME))
            # filter those test that haven't been given.
            if tests_ and test.NAME not in tests_:
                logging.info("- filtered".format(test.NAME))
                continue

            # Each instsance returns a list of sort of executions to evaluate each
            # test sceanrio with different configurations. At leas each test runs 
            # once time. Parameters are build using the queues and messaages parameters
            # given to the constructor.
            t = test(EXCHANGE_NAME, QUEUE_NAME, queues_, messages_)
            for parameters in t.parameters():
                logging.info("- Running with params {}".format(parameters))
                try:
                    t.setUp(**parameters)
                    real, user, sys = t.run(**parameters)
                    results.append(
                        (test.NAME,
                         parameters,
                         real, user, sys,
                         (messages_*queues_)/real))
                    logging.info(_green_message("Finished"))
                except (Exception, TestFailed), e:
                    logging.warning(_red_message("Failed {}".format(str(e))))
                    logging.debug(traceback.format_exc())
                finally:
                    # always call the tearDown method for the specific
                    # test to avoid leave the environment dirty.
                    try:
                        t.tearDown(**parameters)
                    except Exception:
                        logging.warning(_red_message("tearDown failed"))
    finally:
        # We have to remove the AMQP entities created before
        # event there was a exception.
        delete_exchange(EXCHANGE_NAME)
        for i in xrange(0, queues_):
            delete_queue(QUEUE_NAME.format(number=i))
        logging.info('Leaving all AMQP stuff cleaned, removed exchanges and queues used by the tests')

    return results
