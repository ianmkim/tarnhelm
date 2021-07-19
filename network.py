import numpy as np
import pika
import constants

import byte_utils

from func_utils import deprecated
import threading

@deprecated("Use the threaded version of the class")
class _DEP_Network():
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


class Network(threading.Thread):
    def __init__(self, w:int, h:int):
        super(Network, self).__init__()
        self._is_interrupted = False
        self.resource_map = np.zeros((w,h))

    def stop(self):
        self._is_interrupted = True

    def run(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=constants.ADD_RESOURCE_DISCOVERED,exchange_type='fanout')
        self.result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = self.result.method.queue
        self.channel.queue_bind(exchange=constants.ADD_RESOURCE_DISCOVERED, queue=self.queue_name)

        for message in self.channel.consume(self.queue_name, inactivity_timeout=1):
            if self._is_interrupted:
                break
            if not message:
                continue
            try:
                method, properties, body = message
                coords = byte_utils.decode_1d(body)
                self.resource_map[coords[0]][coords[1]] = coords[2]
                print(self.resource_map)
            except Exception as ex:
                print(ex)


if __name__ == "__main__":
    network = Network(800,600)
    network.start()
