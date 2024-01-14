
# Libraries
import pygame
import random
import time
import os
from config import *

SCALE = 1

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character, flip, ai):
        pygame.sprite.Sprite.__init__(self)
        self.ai = ai
        self.health = 0
        self.character = character
        self.current_action = 'idle'
        self.current_frame = 0
        self.last_frame_update = 0
        self.velocity_y = 0
        self.momentum = 0
        self.in_air = True
        self.flip = flip
        self.grid = False
        self.walking = False
        self.crouching = False
        self.jumping = False        
        self.blocking = False
        
        # Sprites
        self.animations = {
            'idle' : self.load_animation('idle'),
            'walk' : self.load_animation('walk'),
            'crouch': self.load_animation('crouch'),
            'jump': self.load_animation('jump'),
            'block' : self.load_animation('block'),
        }

        self.characters = {
            'VENOM': {
                'width'     : 85,
                'height'    : 85,
                'offset'    : (270,200),
            },
            'CAP': {
                'width'     : 75,
                'height'    : 105,
                'offset'    : (285,180),
            },
            'SPIDER': {
                'width'     : 70,
                'height'    : 60,
                'offset'    : (275,230),
            },            
        }

        # Hitbox & Sprite Offset
        self.width = self.characters[self.character]['width'] * SCALE
        self.height = self.characters[self.character]['height'] * SCALE
        self.hitbox = pygame.Rect(x, y, self.width, self.height)
        self.offset = (self.characters[self.character]['offset'][0], self.characters[self.character]['offset'][1])

    def load_animation(self, name):
        animation_list = []
        path = f'SPRITES/{self.character}/{name.upper()}/'
        files = os.listdir(path)
        png_files = [file for file in files if file.endswith('.png')]
        png_files.sort(key=lambda x: int(x.split('.')[0]))    
        #print("PNG Files:", png_files)
        for png_file in png_files:
            full_path = os.path.join(path, png_file)
            img = pygame.image.load(full_path)
            img = pygame.transform.scale(img, (int(img.get_width() * SCALE), int(img.get_height() * SCALE)))
            img.set_colorkey((248,0,248))
            animation_list.append(img)
        #print(f"{name} List:",animation_list)
        return animation_list

    def update(self, tile_list):
        if self.ai:
            self.ai_input()
        else:
            self.get_input()
        self.move(tile_list)
        self.animate()

    def ai_input(self):
        pass

    def get_input(self):
        keys = pygame.key.get_pressed()
        # Walk
        if keys[pygame.K_d] or keys[pygame.K_a]:
            self.flip = keys[pygame.K_a]
            self.walking = True               
        else:
            self.walking = False
        # Crouch
        if keys[pygame.K_s]:
            self.crouching = True
        else:
            self.crouching = False
        # Block
        if keys[pygame.K_b]:
            self.blocking = True
        else:
            self.blocking = False 
        # Jump
        if keys[pygame.K_SPACE] and not self.jumping and not self.in_air:
            self.velocity_y = -GRAVITY*1.5
            self.jumping = True
        else:
            self.jumping = False

    def move(self, tile_list):     

        SPEED = 10
        delta_x = 0
        delta_y = 0

        if not self.in_air:
            if self.walking: delta_x = -SPEED if self.flip else SPEED
            self.momentum = delta_x
        else: 
            delta_x = self.momentum

        # Gravity
        self.velocity_y += 1
        if self.velocity_y > GRAVITY:
            self.velocity_y = GRAVITY
        delta_y += self.velocity_y

        # Collision
        self.in_air = True
        for tile in tile_list:
            #check for collision in x direction
            if tile[1].colliderect(self.hitbox.x + delta_x, self.hitbox.y, self.width, self.height):
                delta_x = 0
                self.momentum = 0
            #check for collision in y direction
            if tile[1].colliderect(self.hitbox.x, self.hitbox.y + delta_y, self.width, self.height):
                #check if below the ground i.e. jumping
                if self.velocity_y < 0:
                    delta_y = tile[1].bottom - self.hitbox.top
                    self.velocity_y = 0
                #check if above the ground i.e. falling
                elif self.velocity_y >= 0:
                    delta_y = tile[1].top - self.hitbox.bottom
                    self.velocity_y = 0
                    self.in_air = False

        # Update plater coordinates
        self.hitbox.x += delta_x
        self.hitbox.y += delta_y

        # Prevents falling from world
        if self.hitbox.bottom > SCREEN_HEIGHT:
            # self.hitbox.bottom = SCREEN_HEIGHT
            # delta_y = 0
            # self.in_air = False
            self.hitbox.x = SCREEN_WIDTH/2
            self.hitbox.y = 200
            self.momentum = 0
            
        
    def animate(self):
        # Disassociate animation interval from game's FPS
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_update < 50:       
            return
        else: 
            self.last_frame_update = current_time
    
        last_frame = len(self.animations[self.current_action]) - 1

        next_action = self.current_action

        if self.in_air:
            next_action = 'jump'  
        else:      
            if self.walking:
                next_action = 'walk'
            elif self.crouching:
                next_action = 'crouch'
            elif self.blocking:
                next_action = 'block'            
            else:
                next_action = 'idle'
        
        if next_action != self.current_action:
            self.current_frame = 0
            self.current_action = next_action

        if self.current_frame < last_frame:
            self.current_frame += 1
        else:            
            self.current_frame = 0
                
    def draw(self, screen):
        screen.blit(
            pygame.transform.flip(self.animations[self.current_action][self.current_frame], self.flip, False), 
            (self.hitbox.x - self.offset[0], self.hitbox.y - self.offset[1])
        )
        if self.grid: 
            print(f"Pos: {self.hitbox.center}| Action: {self.current_action} | Frame: {self.current_frame} | Flip: {self.flip} | Velocity (Y): {self.velocity_y}")
            pygame.draw.rect(screen, WHITE, self.hitbox, 1)
            