from stable_baselines3.ppo import CnnPolicy
from stable_baselines3 import PPO
import supersuit as ss

from lunar_env import env, raw_env, parallel_env
import time

import numpy as np

'''
env = parallel_env()
env = ss.frame_stack_v1(env, 3)
env = ss.pettingzoo_env_to_vec_env_v0(env)
#env = ss.concat_vec_envs_v0(env, 8, num_cpus=4, base_class='stable_baselines3')

model = PPO(CnnPolicy, env, verbose=3, gamma=0.95, n_steps=256, ent_coef=0.0905168, learning_rate=0.00062211, vf_coef=0.042202, max_grad_norm=0.9, gae_lambda=0.99, n_epochs=5, clip_range=0.3, batch_size=256)
model.learn(total_timesteps=2000000)
model.save("policy")
'''

def log(str):
    print(str)

def shell(inp,env):
    if inp[0] == "print":
        roverid = " ".join(inp[1:])
        print(" < ", env.agent_objs[env.agent_name_mapping[roverid]])
    elif inp[0] == "list":
        for item in env.agent_objs:
            print("\t", item)

def interactive():
    log("\n\nInteractive mode enabled")
    log("Help: ")
    log("\t list (lists all agents)")
    log("\t print <Rover ID> (print out details of one agent)")
    log("\t step <x dir> <y dir> <prospect> <mine> <process> (step through)")
    env = raw_env()
    env.reset()
    env.enable_render()
    action_vecs = {}
    while True:
        inp = input("> ")
        if inp == "exit":
            break
        if inp != "":
            inp_split = inp.split(" ")
            if inp_split[0] == "step":
                for agent_name in env.agents:
                    arr = np.array(list(map(int, inp_split[1:])))
                    action_vecs[agent_name] = arr
            else:
                shell(inp_split, env)

            env.step(action_vecs)
        env.draw()
    env.stop()

if __name__ == "__main__":
    interactive()
