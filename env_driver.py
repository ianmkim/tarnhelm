from stable_baselines3.ppo import CnnPolicy
from stable_baselines3 import PPO
import supersuit as ss

from lunar_env import env, raw_env, parallel_env
import time

'''
env = parallel_env()
env = ss.frame_stack_v1(env, 3)
env = ss.pettingzoo_env_to_vec_env_v0(env)
#env = ss.concat_vec_envs_v0(env, 8, num_cpus=4, base_class='stable_baselines3')

model = PPO(CnnPolicy, env, verbose=3, gamma=0.95, n_steps=256, ent_coef=0.0905168, learning_rate=0.00062211, vf_coef=0.042202, max_grad_norm=0.9, gae_lambda=0.99, n_epochs=5, clip_range=0.3, batch_size=256)
model.learn(total_timesteps=2000000)
model.save("policy")
'''

env = raw_env()
env.reset()
env.enable_render()
while True:
    time.sleep(0.2)
    env.draw()
