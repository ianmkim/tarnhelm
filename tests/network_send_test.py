import pika
import sys

sys.path.append("..")

import constants

import numpy as np


def test():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange=constants.ADD_RESOURCE_DISCOVERED, exchange_type='fanout')

    inp = [0, 0, 100]
    message = byte_utils.encode_1d(inp)
    channel.basic_publish(exchange=constants.ADD_RESOURCE_DISCOVERED, routing_key='', body=message)
    print(" [x] Sent %r" % message)
    connection.close()

if __name__ == "__main__":
    test()
