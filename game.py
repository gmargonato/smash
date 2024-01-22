
# Libraries
import pygame
import sys
import random
import time
from pygame.locals import *
from config import *

# Modules
from player import Player
from snow import Snow
from world import World

# PyGamed
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#, RESIZABLE)
pygame.display.set_caption('Smash')
clock = pygame.time.Clock()
FPS = 50

CHARACTERS = ['VENOM','CAP','SPIDER']
player1_character = random.choice(CHARACTERS)
CHARACTERS.remove(player1_character)
player2_character = random.choice(CHARACTERS)

# Objects
world = World(screen)
player = Player(screen, 450, 200, 'CAP', False, False)
player2 = Player(screen, 750, 200, 'CAP', True, True)
snow_effect = Snow(screen)

# Main game loop
while True:

    # HANDLE EVENTS
    for event in pygame.event.get():
        # WINDOW
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()     
        # GAME
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                player.grid = not player.grid
                world.grid = not world.grid
            # if event.key == pygame.K_UP:
            #     FPS = min(500, FPS + 50)
            #     print(FPS)
            # if event.key == pygame.K_DOWN:                
            #     FPS = max(0, FPS - 50)
            #     print(FPS)
            
    # MAP    
    world.draw()

    # UPDATE PLAYER   
    player.update(world.tile_list)
    player.draw()

    player2.update(world.tile_list)
    player2.draw()

    # player2.update(world.tile_list)
    # player2.draw(screen)

    # PARTICLES 
    # snow_effect.snow_flakes_generator()

    pygame.display.flip()
    clock.tick(30)
