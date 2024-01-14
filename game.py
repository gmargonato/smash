
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

# PyGame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#, RESIZABLE)
pygame.display.set_caption('Smash')
clock = pygame.time.Clock()
FPS = 50
last_frame_update = 0
last_key_press_time = 0

# Objects
world = World()
player = Player(SCREEN_WIDTH/3, 200, character='VENOM')
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
            if event.key == pygame.K_UP:
                FPS = min(500, FPS + 50)
                print(FPS)
            if event.key == pygame.K_DOWN:                
                FPS = max(0, FPS - 50)
                print(FPS)
        # PLAYER
        player.get_input(event)
            
    # DRAW MAP    
    #pygame.draw.line(screen, WHITE, (0, 400), (SCREEN_WIDTH, 400), 1)
    world.draw(screen)

    # DRAW PLAYER   
    player.update(world.tile_list)

    player.draw(screen)
    if pygame.time.get_ticks() - last_frame_update > FPS:        
        player.animate()
        last_frame_update = pygame.time.get_ticks()
    
    # PARTICLES
    #snow_effect.snow_flakes_generator()

    pygame.display.flip()
    clock.tick(30)
