
# Libraries
import pygame
import random
import sys
import os
import time
from config import *

animation_info = {
    'ring_out': {
        'scale'     : 1,
        'speed'     : 10,
        'offset'    : (0,0),
    },
}

class Animation():
    def __init__(self, x, y):
        self.animations = {
            'ring_out' : self.load_animation('ring_out')
        }
        self.current = None
        self.frame = 0
        self.pos = [x,y]

    def load_animation(self, name):
        animation_list = []
        path = f'SPRITES/ANIMATIONS/{name.upper()}/'
        files = os.listdir(path)
        png_files = [file for file in files if file.endswith('.png')]
        png_files.sort(key=lambda x: int(x.split('.')[0]))    
        #print("PNG Files:", png_files)
        for png_file in png_files:
            full_path = os.path.join(path, png_file)            
            img = pygame.image.load(full_path)
            scale = animation_info[name]['scale']
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            animation_list.append(img)
        #print(f"{name} List:",animation_list)
        return animation_list
    
    def update(self, animation_name):
        self.current = self.animations[animation_name]
        if self.frame < len(self.current) - 1:           
            self.frame += 1
        else:
            self.current = None
            self.kill()
            
    def draw(self, screen):
        screen.blit(self.current[self.frame], self.pos)