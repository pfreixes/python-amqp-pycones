# AMQP from Python, advanced design patterns

## Build the presentation

```bash
$ pip install -r requirements.txt
$ rst2slides index.rst index.html
```

## Consuming from many queues

```bash
$ ./bin/many_queues run
Running the tests with 50 messages and 200 queues, total messages 10000
Creating the Exchange test.consume_many_queues
Creating 200 queues
Queues created
Running tests
+ Pika_Threads test
- Running with params {'threads': 2}
Finished
- Running with params {'threads': 4}
Finished
- Running with params {'threads': 8}
Finished
- Running with params {'threads': 16}
Finished
- Running with params {'threads': 32}
Finished
- Running with params {'threads': 64}
Finished
+ Pika_Async test
- Running with params {'connections': 2}
Finished
- Running with params {'connections': 4}
Finished
- Running with params {'connections': 8}
Finished
- Running with params {'connections': 16}
Finished
- Running with params {'connections': 32}
Finished
- Running with params {'connections': 64}
Finished
Leaving all AMQP stuff cleaned, removed exchanges and queues used by the tests
+------------+-------------------------+---------+---------+---------+-------+
|Name        |Parameters               |     Real|     User|      Sys|  Msg/s|
+------------+-------------------------+---------+---------+---------+-------+
|Pika_Threads|{'threads': 2}           |    12.68|     3.38|     0.33|    788|
|Pika_Threads|{'threads': 4}           |     5.38|     2.80|     0.33|   1858|
|Pika_Threads|{'threads': 8}           |     3.44|     2.53|     0.42|   2906|
|Pika_Threads|{'threads': 16}          |     2.97|     2.34|     0.45|   3367|
|Pika_Threads|{'threads': 32}          |     2.60|     2.26|     0.53|   3846|
|Pika_Threads|{'threads': 64}          |     2.47|     2.27|     0.72|   4048|
|Pika_Async  |{'connections': 2}       |     9.53|     2.32|     0.17|   1049|
|Pika_Async  |{'connections': 4}       |     4.61|     1.91|     0.17|   2169|
|Pika_Async  |{'connections': 8}       |     2.86|     1.72|     0.14|   3496|
|Pika_Async  |{'connections': 16}      |     2.09|     1.60|     0.14|   4784|
|Pika_Async  |{'connections': 32}      |     1.54|     1.30|     0.14|   6493|
|Pika_Async  |{'connections': 64}      |     1.43|     1.23|     0.13|   6993|
+-----------+-------------------------+---------+---------+---------+--------+
```



