==========================================
AMQP from Python, advanced design patterns
==========================================

* Pau Freixes `@pfreixes`_ and Arnau Orriols `@Arnau_Orriols`_
* Core engineers working at M2M Cloud Factory S.L designing and implementing MIIMETIQ.
* MIIMETIQ is a framework for IoT that uses Python and the following technologies:

  * **Pika**, **Celery**, Flask, Twisted, Tornado, Eve
  * **Rabbitmq**, Mongodb, uwsgi, nginx
  * Ansible
  * PyTest
  * and so on

* This talk is just a good selection of two years using AMQP with Python.
* We will try to move our audience from the basics of AMQP with Python to something called *advanced* 
* The whole talk and code used can be *forked* from git https://github.com/pfreixes/python-amqp-pycones

.. _@pfreixes: https://twitter.com/pfreixes
.. _@Arnau_Orriols: https://twitter.com/Arnau_Orriols

Basics of AMQP
===============

* The Advanced Message Queuing Protocol (AMQP) is an open standard application layer protocol for message-oriented middleware
* Stable specification *1.0* but nobdy uses it, everyone continues on *0.9* specification. Dont ask please.
* One of the most succesfull, and open source, implementation is `RabbitMQ`_. 

.. image:: static/rabbitmq.png

* Basics concepts of AMQP are: *queues*, *consumers*, *publishers*, *exhcanges*, *topics*.
* Basics implementations using previous concepts is just a publish-subscribe pattern 

.. image:: static/publisher-consumer-basic.png


But AMQP is a specification that allow us to build different architectures to model our bussines logic in a decoupled way
getting the adventages of the protocol specification.


.. _RabbitMQ: https://www.rabbitmq.com/

Python meet AMQP
================

Python has a mature and a wide ecosystem of drivers that implement the AMQP protocol to be used your Python code.
Some of them and its main charateristics are:

* `Celery`_ Distributed Task Queue that was initially implemented over AMQP to then become a *bloatware* sofware. Other pieces of sofware such as **librabbitmq**, **kombu** born thanks to Celery and by the same author `Ask`_
* `Pika`_ implemets both asyncronour and syncronous pattern. Luckly several people has continued its development. 
* `txAMQP`_ driver for Twisted. Asycronous pattern.
* `rabbitpy`_ the new kid of `Gavin M Roy`_. He launches it as a main developer of *Pika* may be exhausted with the multi pattern compatibility of Pika.
* *librabbitmq*, *amqp-lib*, *pyamqp*

.. _Celery : https://github.com/celery/celery
.. _Pika : https://github.com/pika/pika
.. _rabbitpy : https://github.com/gmr/rabbitpy
.. _txAMQP : https://pypi.python.org/pypi/txAMQP
.. _Gavin M Roy : https://github.com/gmr
.. _librabbitmq : https://github.com/celery/librabbitmq
.. _Ask : https://github.com/ask


Example of a complex AMQP architecture
======================================

The following image displays a complex AMQP architecture that implements the next features:

* Decouple itensive and CPU bound operations from the Flask code to isolated consumers
* Route the messages published by Devices to the DB applying Authentication, Authoritzation and fair scheduling.
* Notice users looged into the system about new messages such as Device messages in real time.

**PUTT HERE THE IMAGE**

Bottleneck points
=================

The following list are a set of rules to consider about resource contention and bootlenecks that can
apeear implementing AMQP architectures

* Rule 1 ...
* Rule 2 ....
* And *Python* by it self.


Celery
===============

bar

many_queues
===============

foo

conclusions
===============

bar

bar
