import gym
import numpy as np

env = gym.make("FrozenLake-v1")
n_observations = env.observation_space.n
print(env)