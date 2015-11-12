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

from python_amqp.consume_many_queues.pika import Thread as PikaThread
from python_amqp.consume_many_queues.pika import Async as PikaAsync
from python_amqp.consume_many_queues.consume_many_queues_base import TestFailed
from python_amqp.consume_many_queues.consume_many_queues_base import EXCHANGE_NAME, QUEUE_NAME

def _installed_tests():
    return [PikaThread]
    #return [PikaThread, PikaAsync]

# Default test values, they can be override as a paramaters of the
# run function to run them with different values.
QUEUES = 500
MESSAGES = 80

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
    logging.info("Running tests")

    def AMQP_OPERATION(f, args, result):
        if f(*args) != result:
            raise Exception("{}({}) did not return {}".format(f.__name__,
                                                              args,
                                                              result))

    queues_ = queues if queues else QUEUES
    messages_ = messages if messages else MESSAGES
    tests_ = tests

    logging.info('Running the tests with {} messages over {} queues'.format(messages_,
                                                                            queues_))

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
        results = []
        for test in _installed_tests():

            # filter those test that haven't been given.
            if tests_ and test not in tests_:
                logging.debug("`{}` test filtered, skipping it".format(test))
                continue

            # Each instsance returns a list of sort of executions to evaluate each
            # test sceanrio with different configurations. At leas each test runs 
            # once time. Parameters are build using the queues and messaages parameters
            # given to the constructor.
            t = test(EXCHANGE_NAME, QUEUE_NAME, queues_, messages_)
            for parameters in t.parameters():
                logging.info("{} running with params {}".format(test.NAME, parameters))
                try:
                    t.setUp(**parameters)
                    real, user, sys = t.run(**parameters)
                    results.append(
                        (test.NAME,
                         parameters,
                         real, user, sys,
                         (messages_*queues_)/real))
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
        delete_exchange(EXCHANGE_NAME)
        for i in xrange(0, queues_):
            delete_queue(QUEUE_NAME.format(number=i))
        logging.info('Removed exchanges and queues used by the tests')

    return results
