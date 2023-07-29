import pygame, sys
from setting import *
from debug import debug
from level import Level
class Game:
    def __init__(self,action):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Zelda")
        self.clock = pygame.time.Clock()
        self.level = Level()
        main_sound = pygame.mixer.Sound('C:/Users/Hurston/Python_game/5 - level graphics/audio/main.ogg')
        main_sound.set_volume(0.8)
        main_sound.play(loops = -1)

    def run(self,action):
        # while True:
        #     for event in pygame.event.get():
        #         if event.type == pygame.QUIT:
        #             pygame.quit()
        #             sys.exit()
             
        self.screen.fill('black')
        self.level.run(action)
        pygame.display.update()
        self.clock.tick(FPS)
        
 
if __name__ == '__main__':
    game = Game()
    game.run()