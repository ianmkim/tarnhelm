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
from pettingzoo.utils import wrappers
from gym.utils import EzPickle
from pettingzoo.utils.conversions import parallel_wrapper_fn
from pettingzoo.utils import agent_selector

from network import Network, Reality
from constants import *

from rover import Rover

def get_image(path):
    cwd = os.path.dirname(__file__)
    return pygame.image.load(cwd + "/" + path)

def env(**kwargs):
    env = raw_env(**kwargs)
    if env.continuous:
        env = wrappers.ClipOutOfBoundsWrapper(env)
    else:
        env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env

parallel_env = parallel_wrapper_fn(env)

class raw_env(AECEnv, EzPickle):
    metadata = {"render.modes": ["human", "rgb_array"], 'name': "lunar_v0"}

    def __init__(self,
                 rover_speed=500,
                 n_rovers=10,
                 heightmap_img="data/heightmap.png",
                 resource_map="data/resource_map.npy",
                 heightmap = "data/heightmap.npy",
                 screen_width=800,
                 screen_height=600,
                 observation_dims=(500,500),
                 mine_rate=0.1,
                 process_rate=0.1,
                 capacity=0.5):
        EzPickle.__init__(self,rover_speed, n_rovers, heightmap_img, resource_map, heightmap, screen_width, screen_height, observation_dims, mine_rate, process_rate, capacity)
        self.rover_speed = rover_speed
        self.n_rovers = n_rovers

        self.renderOn = False
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.continuous =True

        self.heightmap_img = get_image(heightmap_img)

        self.resource_map = np.load(resource_map)
        self.heightmap = np.load(heightmap)
        self.observed_resource_map = np.zeros(self.resource_map.shape)

        self.agent_objs = [Rover(i, speed=self.rover_speed, mine_rate=mine_rate, process_rate=process_rate, capacity=capacity) for i in range(n_rovers)]
        self.agents = [str(agent) for agent in self.agent_objs]
        self.possible_agents = self.agents[:]

        self._agent_selector = agent_selector(self.agents)
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()

        self.network = Network(self.resource_map.shape)
        self.network.start()

        self.reality = Reality(self.resource_map)
        self.reality.start()

        self.observation_spaces = dict(zip(self.agents, [gym.spaces.Box(low=0, high=255, shape=(100,50), dtype=np.uint8)] * self.n_rovers))

        # action space [x movement, y movement, prospect, mine, process]
        self.action_spaces = dict(
            zip(self.agents,
                [gym.spaces.Box(np.array([-1,-1,0,0,0]), np.array([1,1,1,1,1]), dtype=np.uint8)] * self.n_rovers))

        pygame.init()
        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])
        self.done = False
        self.frames = 0
        self.has_reset = False
        self.closed = False

        self.agent_name_mapping = dict(zip(self.agents, list(range(self.n_rovers))))

    def stop(self):
        self.network.stop()
        self.reality.stop()

    def calc_reward(self):
        return sum([agent.processed for agent in self.agent_objs])


    def step(self, action):
        """
        action is just a dict of action vectors with keys as agent names
        see def rover_act(self, rover, v) for action vector definition
        """
        for k in action.keys():
            #agent = self.agent_selection
            agent = k
            agent_o = self.agent_objs[self.agent_name_mapping[agent]]
            self.rover_act(agent_o, action[agent])
            self._cumulative_rewards[agent] += agent_o.processed
            self._accumulate_rewards()
            self.agent_selection = self._agent_selector.next()

    def rover_act(self, rover, v:np.array):
        """
        Anatomy of V action vector:
        [x movement (-1,1),
         y movement (-1,1),
         prospect at current xy (0,1),
         mine at current xy (0,1),
         process at current xy (0,1)]
        """
        rover.control_raw(v[0:2])
        actions = list(v[2:])
        func_arr = [rover.prospect, rover.mine, rover.process]
        func_arr[actions.index(max(actions))]()


    def reset(self):
        self.has_reset = True
        self.done = False
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self._cumulative_rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self.frames = 0

    def draw(self):
        self.screen.blit(self.heightmap_img, (0,0))
        self.draw_rovers()
        pygame.display.flip()

    def draw_rovers(self):
        for i, rover in enumerate(self.agent_objs):
            self.screen.blit(rover.surf, rover.rect)

    def observe(self, agent) -> np.array:
        """
        Anatomy of observation vector
        [ 0    --- flattened terrain matrix          ---> 2500,
          2500 --- flattened discovered resource map ---> 5000,
          5001 : inventory,
        ]
        """
        # TODO: fix this heaping pile of trash into something that works
        agent_obj = self.agent_objs[self.agent_name_mapping[agent]]
        rad = 25
        height_submap = self.heightmap[agent_obj.x-rad:agent_obj.x+rad, agent_obj.y-rad:agent_obj.y+rad].flatten()
        res_submap = self.resource_map[agent_obj.x-rad:agent_obj.x+rad, agent_obj.y-rad:agent_obj.y+rad].flatten()
        obs_vec = []
        obs_vec.extend(height_submap)
        obs_vec.extend(res_submap)
        obs_vec = np.array(obs_vec)
        obs_vec = obs_vec.reshape((100, 50))
        return obs_vec

    def enable_render(self):
        pygame.display.set_caption("Tarnhelm Simulator")
        #self.screen = pygame.Surface((self.screen_width, self.screen_height))
        #pygame.display.set_mode((self.screen_width, self.screen_height))
        self.renderOn = True
        self.draw()

    def render(self, mode='human'):
        if not self.renderOn:
            self.enable_render()
        self.draw()

    def close(self):
        pass


