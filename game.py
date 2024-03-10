
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
from animation import Animation
from snow import Snow
from world import World

# PyGame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Super Marvel vs Capcom Smash')
clock = pygame.time.Clock()
FPS = 30
grid = False

CHARACTERS = ['RYU','VENOM','CAP1','SPIDER']
choice1 = random.choice(CHARACTERS)
# choice1 = 'SPIDER'
CHARACTERS.remove(choice1)
choice2 = random.choice(CHARACTERS)
# choice2 = 'RYU'

# Objects
world = World('level_0.csv')
player1 = Player(x=450, y=200, character=choice1, flip=False, controller='P1',lives=10,percentage=0)
player2 = Player(x=750, y=200, character=choice2, flip=False, controller='AI',lives=10,percentage=0)
snow_effect = Snow(screen)
projectile_group    = pygame.sprite.Group()
animation_group     = pygame.sprite.Group()

# Main game loop
while True:

    # HANDLE GAME EVENTS
    for event in pygame.event.get():
        # WINDOW
        if event.type == pygame.QUIT: #or player1.lives == 0 or player2.lives == 0:
            pygame.quit()
            sys.exit()     
        # GAME
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                grid = not grid                          
            elif event.key == pygame.K_UP:
                FPS = min(FPS + 5, 60)
                print(f"Current FPS: {FPS}")
            elif event.key == pygame.K_DOWN:
                FPS = max(FPS - 5, 5)
                print(f"Current FPS: {FPS}")

    # MAP    
    world.draw(screen, grid)

    # UPDATE PLAYERS
    player1.update(world.tile_list, player2)
    player1.draw(screen, grid)

    player2.update(world.tile_list, player1)
    player2.draw(screen, grid)

    # HANDLE PLAYER EVENTS
    for player in [player1,player2]:
        for event in player.events:
            event_type = event[0]
            event_location = event[1]

            if event_type == 'projectile': 
                projectile = Projectile(player.controller, event_location[0], event_location[1], -1 if player.flip else 1, player.shoot_type)
                projectile_group.add(projectile)
                player.events.remove(event)
                if player.character == 'CAP1': globals()[f"player{player.controller[-1]}"] = Player(x=player.rect.x, y=player.rect.y, character='CAP2', flip=player.flip, controller='P1',lives=player.lives,percentage=player.percentage)
            elif event_type == 'ring_out':
                animation = Animation('ring_out', event_location[0]-150, event_location[1]-225)
                animation_group.add(animation)
                player.events.remove(event)
            elif event_type == 'hit':
                animation = Animation('hit', event_location[0], event_location[1])
                animation_group.add(animation)
                player.events.remove(event)

    # PROCESS ANIMATIONS
    for a in animation_group:
        a.update()
        a.draw(screen)

    # PROCESS PROJECTILES
    for p in projectile_group:
        p.update()
        p.draw(screen)        
        for player in [player1,player2]:
            if player.rect.colliderect(p.rect):
                if p.owner == player.controller: # Collides with Owner
                    if p.speed == 0 or p.bounce > 0:
                        player1.shoot_cooldown = 0
                        p.kill()
                        new_character = 'CAP1' if player.character == 'CAP2' else player.character
                        globals()[f"player{player.controller[-1]}"] = Player(x=player.rect.x, y=player.rect.y, character=new_character, flip=player.flip, controller=player.controller, lives=player.lives, percentage=player.percentage)
                else: # Collides with Enemy
                    if p.speed == 0: continue
                    if p.type in ['cap_shield']:
                        if player.blocking:
                            p.speed = 0
                            p.rect.y = player.rect.bottom-5
                        else:    
                            player.percentage += 5 
                            p.speed *= -1
                            p.bounce += 1     
                    elif p.type == 'web' and not player.blocking: 
                        p.kill()
                        player.percentage += 5
                        player.stun_cooldown = 300
                        player.walking = False                                                
                        animation = Animation('webbed', player.rect.x-30, player.rect.y-25)
                        animation_group.add(animation)
                    elif p.type == 'hadouken' and not player.blocking: 
                        p.kill()
                        player.percentage += 5                        
                        player.velocity_y = -10
                        player.momentum += 10 * (1 if player.flip else -1)
                    else:                        
                        p.kill()
                
    # PARTICLES
    if not grid: snow_effect.snow_flakes_generator()

    pygame.display.flip()
    clock.tick(FPS)
