import gym
import tensorflow as tf
import numpy as np
from tensorflow import keras
from collections import deque
import time
import random
from training_envi import ZeldaEnvi
from keras.callbacks import TensorBoard
from datetime import datetime
import os
#from tb import CustomTensorBoard
import shutil
from Agent import DQNAgent
from tqdm import tqdm
RANDOM_SEED = 5
tf.random.set_seed(RANDOM_SEED)

env = ZeldaEnvi()
env.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


print("Action Space: {}".format(env.action_space))
print("State space: {}".format(env.observation_space))

################
#Constant variable
DISCOUNT = 0.99
REPLAY_MEMORY_SIZE = 50_000  # How many last steps to keep for model training
MIN_REPLAY_MEMORY_SIZE = 1_000  # Minimum number of steps in a memory to start training
MINIBATCH_SIZE = 64  # How many steps (samples) to use for training
UPDATE_TARGET_EVERY = 5  # Terminal states (end of episodes)
MODEL_NAME = '2x256'
MIN_REWARD = -200  # For model save
MEMORY_FRACTION = 0.20

EPISODES = 10

epsilon = 1
EPSILON_DECAY = 0.99975
MIN_EPSILON = 0.001

AGGREGATE_STATS_EVERY = 50
#################


# An episode a full game
train_episodes = 300
test_episodes = 100

ep_rewards = [0]

#Create repetitive result
random.seed(1)
np.random.seed(1)
tf.random.set_seed(1)


# if not os.path.isdir('models'):
#     os.makedirs('models')
#shutil.rmtree("logs/", ignore_errors = True)
#train_writer = tf.summary.create_file_writer('logs/train')



log_dir = "logs/"
agent = DQNAgent(env,log_dir)
summary_writer = tf.summary.create_file_writer(log_dir)

with summary_writer.as_default():
    for episode in tqdm(range(1, EPISODES + 1),ascii = True, unit = 'episodes'):

        #Update tensorbord step every episode
        agent.tensorboard.step = episode

        #Restarting episode - reset episode reward and step number
        episode_reward = 0
        step = 1

        # Reset environment
        current_state = env.reset()

        # Rest falg and start iterating until episode eneds
        done = False 
        while not done:
            if np.random.random() > epsilon:
                action = np.argmax(agent.get_qs(current_state))
            else:
                action = env.action_space.sample()

            new_state, reward, done, info = env.step(action)

            episode_reward += reward

            #Every step we update replay memory and train main network

            agent.update_replay_memory((current_state,action, reward, new_state,done))
            agent.train(done, step)

            current_state = new_state
            step += 1

        #Appending episode reward to a list and log stats
        ep_rewards.append(episode_reward)
      #  if not episode % AGGREGATE_STATS_EVERY or episode == 1:
        average_reward = sum(ep_rewards[-AGGREGATE_STATS_EVERY:]) / len(ep_rewards[-AGGREGATE_STATS_EVERY:])
        min_reward = min(ep_rewards[-AGGREGATE_STATS_EVERY:])
        max_reward = max(ep_rewards[-AGGREGATE_STATS_EVERY:])

        print(f"Here is the average_reward: {average_reward}, min_reward: {min_reward}, max_reward: {max_reward}\n")
        tf.summary.scalar(name = "average reward",data = average_reward,step = step)
        tf.summary.scalar(name = "min_reward",data = average_reward,step = step)
        tf.summary.scalar(name = "average reward",data = average_reward,step = step)
        tf.summary.scalar(name = "max_reward",data = max_reward,step = step)
        #agent.tensorboard.update_stats(reward_avg=average_reward, reward_min= min_reward, reward_max = max_reward)

        #if min_reward >= MIN_REWARD:
        agent.model.save(f'models/{MODEL_NAME}_{max_reward}max_{average_reward}avg_{min_reward}min_{int(time.time())}.model')

        if epsilon > MIN_EPSILON:
            epsilon *= EPSILON_DECAY
            epsilon = max(MIN_EPSILON,epsilon)


