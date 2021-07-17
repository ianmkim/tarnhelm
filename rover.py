import random
import numpy as np
import pygame

from constants import *
from utils import data_to_screen, screen_to_data
import random

class Rover():
    def __init__(self, id, x=None, y=None, speed=1):
        self.id = id

        self.surf = pygame.Surface((10,10))
        self.surf.fill((255,255,255))

        if x is None or y is None:
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)

        self.screen_x = x
        self.screen_y = y

        self.rect = self.surf.get_rect(center=(self.screen_x, self.screen_y))

        self.x, self.y = screen_to_data((x,y))

        self.speed = speed

    def __str__(self):
        return str("Rover " + self.id)

    def prospect(self):
        pass

    def mine(self):
        pass

    def process(self):
        pass

    def control_raw(self, direction:np.array()):
        if direction[0] < 0:
            out_x = max(direction[0], -self.speed)
        if direction[0] >= 0:
            out_x = min(direction[0], self.speed)

        if direction[1] < 0:
            out_y = max(direction[1], -self.speed)
        if direction[1] >= 0:
            out_y = min(direction[1], self.speed)

        return (out_x, out_y)


