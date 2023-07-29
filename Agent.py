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
from tqdm import tqdm
RANDOM_SEED = 5
tf.random.set_seed(RANDOM_SEED)

# env = ZeldaEnvi()
# env.seed(RANDOM_SEED)
# np.random.seed(RANDOM_SEED)


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

EPISODES = 20000

epsilon = 1
EPSILON_DECAY = 0.99975
MIN_EPSILON = 0.001

AGGREGATE_STATS_EVERY = 50
#################


class DQNAgent:
    def __init__(self,env,log_dir):
        #The main model
        self.check_point_path = "C:/Users/Hurston/Python_game/logs/cp.ckpt"
        self.model = self.create_model((32,3206), env.action_space.n)
        self.model.save_weights(self.check_point_path.format(epoch = 0))

        #Target network
        self.target_model = self.create_model((32,3206), env.action_space.n)
        self.target_model.set_weights(self.model.get_weights())

        #An array with last n steps for training
        self.replay_memory = deque(maxlen = REPLAY_MEMORY_SIZE)
        self.target_update_counter = 0

        #Custome the tensorboard
        #log_dir = "logs/" + datetime.now().strftime("%Y%m%d-%H%M%S")
        self.callbacks = keras.callbacks.ModelCheckpoint(filepath = self.check_point_path,
                                                         save_weights_only = True,
                                                         verbose = 1)
        self.tensorboard = TensorBoard(log_dir=log_dir)

        #Used to count when to update target network with main network's weights


    def create_model(self,state_shape, action_shape):
        """ The agent maps X-states to Y-actions
        e.g. The neural network output is [.1, .7, .1, .3]
        The highest value 0.7 is the Q-Value.
        The index of the highest action (0.7) is action #1.
        """
        learning_rate = 0.001
        init = tf.keras.initializers.HeUniform()
        
        model = keras.Sequential()
        model.add(keras.layers.Dense(24, input_shape=(None,) + state_shape, activation='relu', kernel_initializer=init))
        model.add(keras.layers.Dense(12, activation='relu', kernel_initializer=init))
        model.add(keras.layers.Dense(action_shape, activation='linear', kernel_initializer=init))
        model.compile(loss=tf.keras.losses.Huber(), optimizer=tf.keras.optimizers.Adam(lr=learning_rate), metrics=['accuracy'])
        return model
    
    def update_replay_memory(self,transition):
        self.replay_memory.append(transition)

    def get_qs(self,state):
        return self.model.predict(state.reshape([1, state.shape[0]]))[0]

    #def train(self,env, replay_memory, model, target_model, done):
    def train(self,terminal_state,step):
        #Start training only if certain number of samples is already saved
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE:
            return
        
        #Get a minibatch of random samples from memory replay table

        minibatch = random.sample(self.replay_memory,MINIBATCH_SIZE)

        #Get the current state from minibatch, then query NN model for Q value
        current_states = np.array([transition[0] for transition in minibatch])
        current_qs_list = self.model.predict(current_states)

        #Get the future state from the minibatch, then query NN model for Q values
        # When using target network, query it, otherwise main network should be queried

        new_current_states = np.array([transition[3] for transition in minibatch])
        future_qs_list = self.target_model.predict(new_current_states)

        X = []
        y = []

        #Now enumerate the batches

        for index, (current_state,action, reward, new_current_state,done) in enumerate(minibatch):
            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + DISCOUNT * max_future_q
            else:
                new_q = reward

            #Update Q value to our training data
            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            #Appending to the training data
            X.append(current_state)
            y.append(current_qs)

        self.model.fit(np.array(X),np.array(y),batch_size = MINIBATCH_SIZE,verbose = 0, shuffle = False, callbacks = self.callbacks)
        #self.model.fit(np.array(X),np.array(y),batch_size = MINIBATCH_SIZE,verbose = 0, shuffle = False)

        #Update target network counter every episode

        if terminal_state:
            self.target_update_counter += 1

        #If counter reaches the set values, update the target network with weights of main network
        if self.target_update_counter > UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0


