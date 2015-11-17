from time import sleep
from threading import Thread


import librabbitmq

EXCHANGE = 'demo_fanout'


def single_publisher_small_message_every_(n_seconds):
    message = "x" * 100
    for x in range(100):
        connection = librabbitmq.Connection()
        channel = connection.channel()
        def publish(channel, ex):
            while True:
                channel.basic_publish(message, exchange=EXCHANGE+str(ex))
                sleep(0.005)
        thread = Thread(target=publish, args=[channel, x])
        thread.start()


single_publisher_small_message_every_(0)
