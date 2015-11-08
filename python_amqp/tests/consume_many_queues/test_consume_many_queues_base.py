# -*- coding: utf-8 -*-
"""
Consume Many Queues Base class test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import pytest

from time import sleep
from mock import patch, Mock

from python_amqp.consume_many_queues.consume_many_queues_base import (
    ConsumeManyQueuesBase,
    TestFailed)

class TestConsumeManyQueuesBase(object):

    def test_init(self):
        """ Test the public attributes exposed by the class once it is instantiated """

        class TestExample(ConsumeManyQueuesBase):
            NAME = "Test"
            DESCRIPTION = "Test"

        obj = TestExample("exchange", "queue", 100, 100)
        assert obj.exchange == "exchange"
        assert obj.queue_name == "queue"
        assert obj.queues == 100
        assert obj.messages == 100

    def test_invalid_implementation(self):
        """ Test that invalid implementations can be instantiated """
        class WihoutName(ConsumeManyQueuesBase):
            DESCRIPTION = ""

        class WihoutDescription(ConsumeManyQueuesBase):
            NAME = ""

        for cls in (WihoutName, WihoutDescription):
            try:
                with pytest.raises(ValueError):
                    cls()
            except AssertionError:
                print cls.__name__

    @patch("python_amqp.consume_many_queues.consume_many_queues_base.Publisher")
    @patch("python_amqp.consume_many_queues.consume_many_queues_base.purge_queue")
    @patch("python_amqp.consume_many_queues.consume_many_queues_base.info_queue")
    def test_run(self, info_queue, purge_queue, publisher):
        """ Test the run method """

        class TestExample(ConsumeManyQueuesBase):
            NAME= "Test"
            DESCRIPTION = "Test"

            def __init__(self, *args, **kwargs):
                ConsumeManyQueuesBase.__init__(self, *args, **kwargs)
                self.setUp_called = False
                self.test_called = False
                self.tearDown_called = False

            def test(self, *args, **kwargs):
                self.test_called = True
                sleep(0.1)  # simulate a while

            def _all_messages_published(self):
                # we override this message to return True
                return True

 
        # The test run was good, therefore it left 0 messages to consume
        info_queue.return_value = {'messages': 0}

        # Instantiate the test and run it
        test = TestExample("exchange", "queue", 10, 100)
        real , user, sys = test.run()

        # check tat we tried to publish the messages for the test, and then 
        # we check that all messages were consumed
        assert publisher.return_value.publish.call_count == 100
        assert info_queue.call_count == 10

        # at last check that we monitored the times
        assert real + user + sys > 0.0

        # all test methods were called
        assert test.test_called

    @patch("python_amqp.consume_many_queues.consume_many_queues_base.Publisher")
    @patch("python_amqp.consume_many_queues.consume_many_queues_base.purge_queue")
    @patch("python_amqp.consume_many_queues.consume_many_queues_base.info_queue")
    def test_run_purge_is_always_called(self, info_queue, purge_queue, publisher):
        """ Test when the test failed purge is also called"""

        class TestExample(ConsumeManyQueuesBase):
            NAME = "Test"
            DESCRIPTION = "Test"

            def test(self, *args, **kwargs):
                # simulate a exception
                raise Exception()

            def _all_messages_published(self):
                # we override this message to return True
                return True

        # The test run was bad, therefore it left all messages to consume
        info_queue.return_value = {'messages': 100}

        with pytest.raises(Exception):
            TestExample("exchange", "queue", 10, 100).run()

        # check tat we tried to publish the messages for the test, and then 
        # we check that the messages were still to be consumed and we tried
        # to purge the queue
        assert info_queue.call_count == 10
        assert purge_queue.call_count == 10

    @patch("python_amqp.consume_many_queues.consume_many_queues_base.Publisher")
    @patch("python_amqp.consume_many_queues.consume_many_queues_base.purge_queue")
    @patch("python_amqp.consume_many_queues.consume_many_queues_base.info_queue")
    def test_run_left_messages_to_consumee(self, info_queue, purge_queue, publisher):
        """ Test when the test failed because left messages to consume"""

        class TestExample(ConsumeManyQueuesBase):
            NAME = "Test"
            DESCRIPTION = "Test"

            def test(self, *args, **kwargs):
                # simulate a amount of time
                return sleep(0.1)

            def _all_messages_published(self):
                # we override this message to return True
                return True

        # The test run was bad, therefore it left all messages to consume
        info_queue.return_value = {'messages': 100}

        with pytest.raises(TestFailed):
            TestExample("exchange", "queue", 10, 100).run()

        # check tat we tried to publish the messages for the test, and then 
        # we check that the messages were still to be consumed and we tried
        # to purge the queue even.
        assert info_queue.call_count == 10
        assert purge_queue.call_count == 10
