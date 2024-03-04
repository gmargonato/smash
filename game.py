
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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Super Marvel vs Capcom Smash')
clock = pygame.time.Clock()
FPS = 30

# Objects
world = World(screen)
player1 = Player(450, 200, 'CAP_SHIELD',False, 'P1')
player2 = Player(750, 200, 'RYU',       True,  'AI')
snow_effect = Snow(screen)
projectile_group = pygame.sprite.Group()

# Main game loop
while True:

    # HANDLE EVENTS
    for event in pygame.event.get():
        # WINDOW
        if event.type == pygame.QUIT: #or player1.lives == 0 or player2.lives == 0:
            pygame.quit()
            sys.exit()     
        # GAME
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                player1.grid = not player1.grid
                player2.grid = not player2.grid
                world.grid = not world.grid                
            elif event.key == pygame.K_UP:
                FPS = min(FPS + 5, 60)
                print(f"Current FPS: {FPS}")
            elif event.key == pygame.K_DOWN:
                FPS = max(FPS - 5, 5)
                print(f"Current FPS: {FPS}")

    # MAP    
    world.draw()

    # UPDATE PLAYERS
    player1.update(world.tile_list, player2)
    player1.draw(screen)

    player2.update(world.tile_list, player1)
    player2.draw(screen)

    # PROJECTILES
    if player1.shoot: 
        projectile = Projectile('P1', player1.hitbox.x, player1.hitbox.y, -1 if player1.flip else 1, player1.shoot_type)
        projectile_group.add(projectile)
        player1.shoot = False
        
    for p in projectile_group:
        p.update()
        p.draw(screen)
        if p.get_owner() == 'P1':
            if player1.shoot_cooldown <= 0: p.kill()        
            # Player 1 retrieves
            if player1.hitbox.colliderect(p.rect) and player1.shoot_type == 'boomerang' and (p.bounce_count > 0 or p.speed == 0):
                    player1.shoot_cooldown = 0
                    p.kill()                            
            # Player 2 hit
            elif player2.hitbox.colliderect(p.rect) and p.speed > 0:            
                if not player2.blocking: 
                    player2.percentage += 5
                    p.kill()
                else: 
                    p.speed = 0                
                    p.rect.y = player2.hitbox.bottom-5
        else: # Owner = 'P2'      
            if player2.shoot_cooldown <= 0: p.kill()      
            # Player 2 retrives
            if player2.hitbox.colliderect(p.rect) and player2.shoot_type == 'boomerang' and p.bounce_count > 0:                            
                player2.shoot_cooldown = 0
                p.kill()    
            # Player 1 hit
            elif player1.hitbox.colliderect(p.rect) and p.speed > 0:
                p.kill()
                if not player1.blocking: player1.percentage += 5
        
    # PARTICLES
    if not world.grid: snow_effect.snow_flakes_generator()

    pygame.display.flip()
    clock.tick(FPS)
