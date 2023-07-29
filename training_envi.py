import gym 
from gym import spaces
from player import Player
from enemy import Enemy
import pygame
from collections import deque
from setting import *
import numpy as np
import sys
from level import Level
GOAL_EXP = 3200

class ZeldaEnvi(gym.Env):
    RETURN_IMAGES = True
    def __init__(self):
        super(ZeldaEnvi,self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(6)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=-2000, high=2000,
                                            shape=(6 + 1375,), dtype=np.float32)
        self.count = 0
        
    def step(self, action):
        self.prev_actions.append(action)
        
        
        health_check = self.level.player.health
        enemy_check = self.level.enemy.health
        #print(self.done)
        
        self.count += 1
        if health_check >= 0 or pygame.K_q:
            self.level.run(action)
            pygame.display.update()
            self.clock.tick(FPS)
            
            if not(self.level.enemy.vulnerable):
                self.reward += 50
                if (self.level.enemy.health <= 0):
                    self.reward += 100
            if (self.level.enemy.vulnerable) and (action == 5):
                self.reward -= 1
            
            if health_check < 0 or self.count >= 1000:
                self.count = 0
                self.done = True
                self.reward = -100
                pygame.init()
                self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
                pygame.display.set_caption("Zelda")
                self.clock = pygame.time.Clock()
                self.level = Level()
                self.level.run(action)
                pygame.display.update()
                self.clock.tick(FPS)
            
        info = {}
        health_player = self.player.health
        health_enemy = self.enemy.health
        player_position = self.player.rect.center
        player_direction = self.player.direction
        enemy_direction = self.enemy.direction
        enemy_position = self.enemy.rect.center

        distance_bet_ene_player_x = player_position[0] - enemy_position[0]
        distance_bet_ene_player_y = player_position[1] - enemy_position[1]
        vec_ene_play = player_direction - enemy_direction

        self.observation = [distance_bet_ene_player_x,distance_bet_ene_player_y,player_position[0],player_position[1],vec_ene_play[0],vec_ene_play[1]] + list (self.prev_actions)
        self.observation = np.array(self.observation,dtype = np.float32)
        info = {}
        return self.observation, self.reward,self.done,info

    def reset(self):
        self.done = False
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Zelda")
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.reward = 0
        
        self.player = self.level.player
        self.enemy = self.level.enemy
        exp = self.player.exp
        health_player = self.player.health
        mana_player = self.player.energy
        health_enemy = self.enemy.health
        player_position = self.player.rect.center
        player_direction = self.player.direction
        enemy_direction = self.enemy.direction
        enemy_position = self.enemy.rect.center
        distance_bet_ene_player_x = player_position[0] - enemy_position[0]
        distance_bet_ene_player_y = player_position[1] - enemy_position[1]
        vec_ene_play = player_direction - enemy_direction

        self.prev_actions = deque(maxlen=GOAL_EXP)

        for i in range(GOAL_EXP):
            self.prev_actions.append(-1)
        
        self.observation = [distance_bet_ene_player_x,distance_bet_ene_player_y,player_position[0],player_position[1],vec_ene_play[0],vec_ene_play[1]] + list (self.prev_actions)
        self.observation = np.array(self.observation,dtype=np.float32)
        
        #We will return player position, enemy position, enemy direction, the exp, 
        return self.observation