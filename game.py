
# Libraries
import pygame
import sys
import random
import time
from pygame.locals import *
from config import *

# Modules
from player import Player
from projectile import Projectile
from snow import Snow
from world import World

# PyGame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#, RESIZABLE)
pygame.display.set_caption('Super Marvel vs Capcom Smash')
clock = pygame.time.Clock()
FPS = 60

# CHARACTERS = ['VENOM','CAP','SPIDER']
# player1_character = random.choice(CHARACTERS)
# CHARACTERS.remove(player1_character)
# player2_character = random.choice(CHARACTERS)

# Objects
world = World(screen)
player1 = Player(450, 200, 'CAP_SHIELD', flip=False, ai=False)
player2 = Player(750, 200, 'CAP_SHIELD', flip=True,  ai=True)
snow_effect = Snow(screen)
projectile_group = pygame.sprite.Group()

# Main game loop
while True:

    # HANDLE EVENTS
    for event in pygame.event.get():
        # WINDOW
        if event.type == pygame.QUIT or player1.lives == 0 or player2.lives == 0:
            pygame.quit()
            sys.exit()     
        # GAME
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                player1.grid = not player1.grid
                player2.grid = not player2.grid
                world.grid = not world.grid

    # MAP    
    world.draw()

    # UPDATE PLAYERS
    player1.update(world.tile_list, player2)
    player1.draw(screen)

    player2.update(world.tile_list, player1)
    player2.draw(screen)

    # UPDATE GROUPS
    if player1.shoot: 
        projectile = Projectile(player1.hitbox.x, player1.hitbox.y, -1 if player1.flip else 1, player1.shoot_type)
        projectile_group.add(projectile)
        player1.shoot = False    
    projectile_group.update()
    projectile_group.draw(screen)

    # CHECK COLLISION WITH PROJECTILE
    for p in projectile_group:
        if player1.hitbox.colliderect(p.rect) and p.bounce_count > 0: 
            p.kill()
            player1.shoot_cooldown = 0

    # PARTICLES 
    # snow_effect.snow_flakes_generator()

    pygame.display.flip()
    clock.tick(30)
