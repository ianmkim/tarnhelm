import numpy as np
import pika
import constants

import byte_utils

class Network():
    def __init__(self, w, h):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=constants.ADD_RESOURCE_DISCOVERED,exchange_type='fanout')
        self.result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = self.result.method.queue
        self.channel.queue_bind(exchange=constants.ADD_RESOURCE_DISCOVERED, queue=self.queue_name)

        self.resource_map = np.zeros((w,h))

        def callback(ch, method, properties, body):
            coords = byte_utils.decode_1d(body)
            print("received body " + coords)
            resource_map[coords[0]][coords[1]] = coords[2]

        print("started basic_consume")
        self.channel.basic_consume(self.queue_name, on_message_callback=callback, auto_ack=True)

