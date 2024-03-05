
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

player1 = Player(x=450, y=200, character='CAP1', flip=False, controller='P1',lives=3,percentage=0)
player2 = Player(x=750, y=200, character='RYU', flip=False, controller='AI',lives=3,percentage=0)
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
        if player1.character == 'CAP1':
            player1 = Player(x=player1.hitbox.x, y=player1.hitbox.y, character='CAP2', flip=player1.flip, controller='P1',lives=player1.lives,percentage=player1.percentage)

    for p in projectile_group:
        p.update()
        p.draw(screen)
        for player in [player1,player2]:
            if player.hitbox.colliderect(p.rect):
                if p.owner == player.controller: # Collides with Owner
                    if p.speed == 0 or p.bounce > 0:
                        player1.shoot_cooldown = 0
                        p.kill()
                        new_character = 'CAP1' if player.character == 'CAP2' else player.character
                        globals()[f"player{player.controller[-1]}"] = Player(x=player.hitbox.x, y=player.hitbox.y, character=new_character, flip=player.flip, controller=player.controller, lives=player.lives, percentage=player.percentage)

                else: # Collides with Enemy
                    if p.speed == 0: continue
                    if p.type == 'boomerang':
                        if player.blocking:
                            p.speed = 0
                            p.rect.y = player.hitbox.bottom-5
                        else:    
                            player.percentage += 5 
                            p.speed *= -1
                            p.bounce += 1                        
                    else:
                        if not player.blocking: player.percentage += 5
                        p.kill()
                    
    # PARTICLES
    if not world.grid: snow_effect.snow_flakes_generator()

    pygame.display.flip()
    clock.tick(FPS)
