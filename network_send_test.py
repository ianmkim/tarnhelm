import pika
import sys
import constants
import byte_utils

import numpy as np

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=constants.ADD_RESOURCE_DISCOVERED, exchange_type='fanout')

while True:
    inp = np.array(list(map(int, input("> ").split(" "))))
    print(inp)
    message = byte_utils.encode_1d(inp)
    channel.basic_publish(exchange=constants.ADD_RESOURCE_DISCOVERED, routing_key='', body=message)
    print(" [x] Sent %r" % message)
connection.close()

