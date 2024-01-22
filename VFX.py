
# Libraries
import pygame
import random
import sys
import os
import time
from config import *

class VFX:
    def __init__(self, screen):
        self.screen = screen
        self.scale = 0.25
        self.animations = {
            'ring_out' : self.load_animation('ring_out'),            
        }

    def load_animation(self, name):
        animation_list = []
        path = f'SPRITES/VFX/{name.upper()}/'
        files = os.listdir(path)
        png_files = [file for file in files if file.endswith('.png')]
        png_files.sort(key=lambda x: int(x.split('.')[0]))    
        #print("PNG Files:", png_files)
        for png_file in png_files:
            full_path = os.path.join(path, png_file)            
            img = pygame.image.load(full_path)
            img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
            animation_list.append(img)
        #print(f"{name} List:",animation_list)
        return animation_list
    
    def play_animation(self, effect, flip, x, y):

        frames = self.animations.get(effect, [])
        if frames:
            for frame in self.animations[effect]:  
                # Adjustments if Ring-Out effect
                if effect == 'ring_out':
                    y = SCREEN_HEIGHT-200

                # Print the effect on-screen
                self.screen.blit(
                    pygame.transform.flip(frame, flip, False),
                    (x, y)
                )
                pygame.display.flip()
                pygame.time.delay(5)