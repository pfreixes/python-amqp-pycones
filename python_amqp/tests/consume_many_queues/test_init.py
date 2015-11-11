# -*- coding: utf-8 -*-
"""
Consume Many Queues
~~~~~~~~~~~~~~~~~~~
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import pytest

from time import sleep
from mock import patch, Mock

from python_amqp.consume_many_queues import info, run
from python_amqp.consume_many_queues import QUEUES, MESSAGES
from python_amqp.consume_many_queues import list as list_tests

def test_info():
    """ Get info from Thread pika implemenation """
    from python_amqp.consume_many_queues.pika import Thread
    doc_string = info(Thread.NAME)
    assert doc_string == Thread.__doc__

def test_info_not_found():
    assert info("foo") == "Test foo have not found"

def test_list_tests():
    """ Just test that returns a list of strings """
    list_ = list_tests()
    for doc in list_:
        assert isinstance(doc, str)
    
class TestRun(object):

    @patch("python_amqp.consume_many_queues._installed_tests")
    @patch("python_amqp.consume_many_queues.create_exchange")
    @patch("python_amqp.consume_many_queues.create_queue")
    @patch("python_amqp.consume_many_queues.set_binding")
    @patch("python_amqp.consume_many_queues.delete_exchange")
    @patch("python_amqp.consume_many_queues.delete_queue")
    def test_run_all_tests(self, delete_queue, delete_exchange, set_binding,
                           create_queue, create_exchange, _installed_tests):
        """ Test run method run all tests"""

        # We declare twice tests that will be installed over the
        # TESTS global variable. Thet will be called by the run
        # function.
        class Foo:
            NAME = "Foo"
            DESCRIPTION = "Foo"
            def __init__(self, *args, **kwargs):
                pass
            def setUp(self, *args, **kwargs):
                pass
            def tearDown(self, *args, **kwargs):
                pass
            def parameters(self, *args, **kwargs):
                return [{}]
            def run(self, *args, **kwargs):
                return 1, 2, 3

        class Bar:
            NAME = "Bar"
            DESCRIPTION = "Bar"
            def __init__(self, *args, **kwargs):
                pass
            def setUp(self, *args, **kwargs):
                pass
            def tearDown(self, *args, **kwargs):
                pass
            def parameters(self, *args, **kwargs):
                return [{}]
            def run(self, *args, **kwargs):
                return 3, 2, 1


        create_exchange.return_value = True
        create_queue.return_value = True
        set_binding.return_value = True

        _installed_tests.return_value = [Foo, Bar]

        results = run()

        assert results == [('Foo', {}, 1, 2, 3), ('Bar', {}, 3, 2, 1)]
        assert delete_exchange.call_count == 1
        assert create_exchange.call_count == 1
        assert create_queue.call_count == QUEUES
        assert delete_queue.call_count == QUEUES
        assert set_binding.call_count == QUEUES
