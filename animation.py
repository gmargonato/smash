
# Libraries
import pygame
import random
import sys
import os
import time
from config import *

animation_list = {
    'ring_out': {
        'path'      : "/Users/gabrielmargonato/Documents/Python Scripts/smash/SPRITES/ANIMATIONS/RING_OUT",
        'scale'     : 1
    },
    'hit': {
        'path'      : "/Users/gabrielmargonato/Documents/Python Scripts/smash/SPRITES/ANIMATIONS/HIT",
        'scale'     : 0.5
    },
    'webbed': {
        'path'      : "/Users/gabrielmargonato/Documents/Python Scripts/smash/SPRITES/ANIMATIONS/WEBBED",
        'scale'     : 1
    },
}

class Animation(pygame.sprite.Sprite):
    def __init__(self, name, x, y):
        pygame.sprite.Sprite.__init__(self)      
        self.name = name
        self.x = x
        self.y = y
        self.index = 0
        self.frames = self.load_images()        
        self.image = self.frames[self.index]
        self.last_frame_update = 0
        
    def load_images(self):
        images = []
        folder_path = animation_list[self.name]['path']
        scale = animation_list[self.name]['scale']
        for file_name in sorted(os.listdir(folder_path)):
            if file_name.endswith('.png'):
                loaded_image = pygame.image.load(os.path.join(folder_path, file_name))#.convert_alpha()
                image = pygame.transform.scale(loaded_image, (int(loaded_image.get_width() * scale), int(loaded_image.get_height() * scale)))
                image.set_colorkey((0,0,0))
                images.append(image)
        return images

    def update(self):
        last_frame = len(self.frames) - 1
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_update < 50:
            return
        else: 
            self.last_frame_update = current_time
            self.index += 1
            if self.index == last_frame:
                self.kill()
            self.image = self.frames[self.index]

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y)) #, special_flags = pygame.BLEND_SUB or BLEND_ADD