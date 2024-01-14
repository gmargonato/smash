
# Libraries
import pygame
import random
import time
import os
from config import *

SCALE = 1

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character):
        pygame.sprite.Sprite.__init__(self)
        self.character = character
        self.current_action = 'idle'
        self.current_frame = 0
        self.velocity_y = 0
        self.momentum = 0
        self.flip = False
        self.grid = False
        self.walking = False
        self.crouching = False
        self.jumping = False
        self.falling = True
        self.attacking = False
        self.blocking = False
        
        # Sprites
        self.animations = {
            'idle' : self.load_animation('idle'),
            'walk' : self.load_animation('walk'),
            'crouch': self.load_animation('crouch'),
            'jump': self.load_animation('jump'),
            'block' : self.load_animation('block'),
            # 'atk': self.load_animation('atk'),
        }

        self.hitboxes = {
            'VENOM': (85,85),
        }

        # Hitbox
        self.hitbox = pygame.Rect(x, y, self.hitboxes[character][0]*SCALE, self.hitboxes[character][1]*SCALE)

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

        SPEED = 10
        delta_x = 0
        delta_y = 0

        # if self.hitbox.x >= 1295:   self.hitbox.x = -15
        # if self.hitbox.x <= -20:    self.hitbox.x = 1290

        if not self.falling:
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
        for tile in tile_list:
            #check for collision in x direction
            if tile[1].colliderect(self.hitbox.x + delta_x, self.hitbox.y, self.hitboxes[self.character][0], self.hitboxes[self.character][1]):
                delta_x = 0
            #check for collision in y direction
            if tile[1].colliderect(self.hitbox.x, self.hitbox.y + delta_y, self.hitboxes[self.character][0], self.hitboxes[self.character][1]):
                #check if below the ground i.e. jumping
                if self.velocity_y < 0:
                    delta_y = tile[1].bottom - self.hitbox.top
                    self.velocity_y = 0
                #check if above the ground i.e. falling
                elif self.velocity_y >= 0:
                    delta_y = tile[1].top - self.hitbox.bottom
                    self.velocity_y = 0

        # Update plater coordinates
        self.hitbox.x += delta_x
        self.hitbox.y += delta_y

        # Prevents falling from world
        if self.hitbox.bottom > SCREEN_HEIGHT:
            self.hitbox.bottom = SCREEN_HEIGHT
            delta_y = 0
            self.falling = False
            self.jumping = False
        
    def get_input(self, event):
        # next_action = self.current_action
        # Key pressed
        if event.type == pygame.KEYDOWN:                                  
            if event.key in [pygame.K_a, pygame.K_d]:
                self.flip = pygame.key.get_pressed()[pygame.K_a]                
                self.walking = True
                # next_action = 'walk'
            if event.key == pygame.K_s:
                self.crouching = True
                # next_action = 'crouch'
            if event.key == pygame.K_b:
                self.blocking = True
                # next_action = 'block'
            if event.key == pygame.K_SPACE and (not self.jumping):
                self.velocity_y = -GRAVITY
                self.jumping = True
                self.falling = True
        # Key released
        elif event.type == pygame.KEYUP:                
            if event.key in [pygame.K_d, pygame.K_a]:
                self.walking = False 
                # next_action = 'idle'
            if event.key == pygame.K_s:
                self.crouching = False
                # next_action = 'idle'
            if event.key == pygame.K_b:
                self.blocking = False
                # next_action = 'idle'
            if event.key == pygame.K_SPACE:
                self.jumping = False
        # Finally, update the action
        # self.update_action(next_action)

    def update_action(self, new_action):
        if new_action != self.current_action:
            self.current_frame = 0
            self.current_action = new_action

    def animate(self):
        last_frame = len(self.animations[self.current_action]) - 1
        next_action = 'idle'
        if self.walking:    next_action = 'walk'
        elif self.crouching:   next_action = 'crouch'
        elif self.blocking: next_action = 'block'
        
        if self.current_frame < last_frame:
            self.current_frame += 1
        else:
            self.current_action = next_action
            self.current_frame = 0
            
    def draw(self, screen):
        screen.blit(
            pygame.transform.flip(self.animations[self.current_action][self.current_frame], self.flip, False), 
            (self.hitbox.x -270, self.hitbox.y - 200)
            # (self.hitbox.x -0, self.hitbox.y - 0)
        )
        if self.grid: 
            print(f"Pos: {self.hitbox.center}| Action: {self.current_action} | Frame: {self.current_frame} | Flip: {self.flip} | Velocity (Y): {self.velocity_y}")
            pygame.draw.rect(screen, WHITE, self.hitbox, 1)
            