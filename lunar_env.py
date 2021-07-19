import os
from os import path as os_path

import pygame
import pymunk
import pymunk.pygame_util

import math
import numpy as np

import gym
from gym.utils import seeding

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers
from gym.utils import EzPickle
from pettingzoo.utils.conversions import parallel_wrapper_fn

from rover import Rover

def get_image(path):
    cwd = os.path.dirname(__file__)
    return pygame.image.load(cwd + "/" + path)

def env(**kwargs):
    env = raw_env(**kwargs)
    if env.coontinuous:
        env = wrappers.ClipOutOfBoundsWrapper(env)
    else:
        env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env

class raw_env(AECEnv, EzPickle):
    metadata = {"render.modes": ["human", "rgb_array"], 'name': "lunar_v0"}

    def __init__(self,
                 rover_speed=1,
                 n_rovers=10,
                 heightmap_img="data/heightmap.png",
                 resource_map="data/resource_map.npy",
                 heightmap = "data/heightmap.npy",
                 screen_width=800,
                 screen_height=600,
                 observation_dims=(500,500)):
        self.rover_speed = rover_speed
        self.n_rovers = n_rovers

        self.renderOn = False
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.heightmap_img = get_image(self.heightmap_img)

        self.resource_map = np.load(resource_map)
        self.heightmap = np.load(heightmap)
        self.observed_resource_map = np.zeros(resource_map.shape)

        self.agent_objs= [Rover(i, speed=self.rover_speed) for i in range(n_rovers)]
        self.agents = [str(agent) for agent in agent_objs]

        self.network = Network(resourec_map.shape)
        self.network.start()

        self.observation_spaces = dict(
            zip(self.agents, [gym.spaces.Box(low=0, high=100, shape=observation_dims, dtype=np.float16] * self.n_rovers)))

        # action space [x movement, y movement, prospect, mine, process]
        self.action_spaces = dict(
            zip(self.agents,
                [gym.spaces.Box(np.array(-1,-1,0,0,0), np.array(1,1,1,1,1), dtype=np.uint8)] * self.n_rovers))

        pygame.init()
        self.done = False
        self.frames = 0
        self.has_reset = False
        self.closed = False

        self.agent_name_mapping = dict(zip(self.agents, list(range(self.n_rovers))))
        self._agent_selector = agent_selector(self.agents)

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)

        action = np.asarray(action)
        agent = self.agent_selection
        self.rover_act(self.agent_objs[self.agent_name_mapping[agent]], action)

    def rover_act(self, rover, v):


    def reset(self):
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.draw()

        self.has_reset = True
        self.done = False
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self._cumulative_reward = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self.frames = 0

    def draw(self):
        self.screen.blit(self.heightmap_img, (0,0))
        self.draw_rovers()

    def draw_rovers(self):
        for i, rover in enumerat(self.agent_objs):
            self.screen.blit(rover.surf, rover.rect)

    def observe(self, agent):
        pass

    def enable_render(self):
        pygame.display.set_caption("Tarnhelm Simulator")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.renderOn = True
        self.draw()


    def render(self, mode='human'):
        if not self.renderOn:
            self.enable_render()
        self.draw()

    def state(self):
        pass

    def close(self):
        pass


