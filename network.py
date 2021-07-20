import numpy as np
import pika
import constants

import utils.byte_utils as byte_utils

from utils.func_utils import deprecated
import threading

@deprecated("Use the threaded version of the class")
class _DEP_Network():
    def __init__(self, shape):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=constants.ADD_RESOURCE_DISCOVERED,exchange_type='fanout')
        self.result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = self.result.method.queue
        self.channel.queue_bind(exchange=constants.ADD_RESOURCE_DISCOVERED, queue=self.queue_name)

        self.resource_map = np.zeros(shape)

        def callback(ch, method, properties, body):
            coords = byte_utils.decode_1d(body)
            print("received body " + coords)
            resource_map[coords[0]][coords[1]] = coords[2]

        print("started basic_consume")
        self.channel.basic_consume(self.queue_name, on_message_callback=callback, auto_ack=True)

class Reality(threading.Thread):
    def __init__(self, groundtruth):
        super(Reality, self).__init__()
        self.groundtruth = groundtruth
        self._is_interrupted = False

    def stop(self):
        self._is_interrupted = True

    def run(self) -> float:
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=constants.REQUEST_GROUNDTRUTH, exchange_type="fanout")

        self.result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = self.result.method.queue
        self.channel.queue_bind(exchange=constants.REQUEST_GROUNDTRUTH, queue=self.queue_name)

        for message in self.channel.consume(self.queue_name, inactivity_timeout=1):
            if self._is_interrupted:
                break
            if not message[2]:
                continue
            method, prop, body = message
            str_body = body.decode("utf-8").split(" ")
            queue_name = str_body[0]
            coords = list(map(int, str_body[1:]))
            gt_value = self.groundtruth[coords[0]][coords[1]]
            self.channel.basic_publish(exchange='', routing_key=queue_name, body=str(gt_value))

        self.connection.close()



class Network(threading.Thread):
    def __init__(self, shape, error=0.05):
        super(Network, self).__init__()
        self._is_interrupted = False
        self.resource_map = np.zeros(shape)
        self.error = error

    def stop(self):
        self._is_interrupted = True

    def prospect(self, x, y) -> float:
        # TODO: need to implement prospecting error
        return resource_map_gt[x][y]

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
                self.resource_map[int(coords[0])][int(coords[1])] = coords[2]
            except Exception as ex:
                continue

        self.connection.close()


if __name__ == "__main__":
    network = Network((800,600))
    network.start()
