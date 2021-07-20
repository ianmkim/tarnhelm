import random
import numpy as np
import pygame
import pika

from constants import *
import constants
from utils.utils import data_to_screen, screen_to_data
from utils import byte_utils
import random

class Rover():
    def __init__(self, id, x=None, y=None, speed=1, mine_rate=0.1, process_rate=0.1, capacity=0.5):
        self.id = id

        self.surf = pygame.Surface((10,10))
        self.surf.fill((255,255,255))

        if x is None or y is None:
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)

        self.screen_x = x
        self.screen_y = y
        self.x, self.y = screen_to_data((x,y))

        self.rect = self.surf.get_rect(center=(self.screen_x, self.screen_y))

        self.capacity = capacity
        self.mine_rate = mine_rate
        self.process_rate = process_rate

        self.inventory = 0
        self.processed = 0

        self.speed = speed

    def __str__(self):
        return str("Rover " + self.id)

    def report(self, amount):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange=constants.ADD_RESOURCE_DISCOVERED, exchange_type="fanout")

        send_byte = byte_utils.encode_1d(np.array([self.x, self.y, amount]))

        channel.basic_publish(exchange=constants.ADD_RESOURCE_DISCOVERED, routing_key='', body = send_byte)
        connection.close()

    def prospect(self):
        x, y = self.x, self.y
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

        channel = connection.channel()
        channel.exchange_declare(exchange=constants.REQUEST_GROUNDTRUTH, exchange_type="fanout")

        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        send_str = queue_name + " " + str(x) + " " + str(y)
        channel.basic_publish(exchange=constants.REQUEST_GROUNDTRUTH, routing_key='', body=send_str)

        float_body = 0
        for message in channel.consume(queue_name, inactivity_timeout=1):
            try:
                method, prop, body = message
                float_body = float(body)
                break
            except Exception as ex:
                continue
        connection.close()
        return float_body

    def mine(self):
        x, y = self.x, self.y
        res_at_coords = self.prospect()
        if res_at_coords-self.mine_rate > 0 and self.inventory + self.mine_rate <= self.capacity:
            self.inventory += self.mine_rate
            return True
        return False

    def process(self):
        if self.inventory - self.process_rate >=0:
            self.inventory -= self.process_rate
            self.processed += self.process_rate
            return True
        return False

    def control_raw(self, direction:np.array):
        if direction[0] < 0:
            out_x = max(direction[0], -self.speed)
        if direction[0] >= 0:
            out_x = min(direction[0], self.speed)

        if direction[1] < 0:
            out_y = max(direction[1], -self.speed)
        if direction[1] >= 0:
            out_y = min(direction[1], self.speed)

        return (out_x, out_y)


