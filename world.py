
# Libraries
import pygame
import random
import time
import os
import csv
from config import *

tile_images = {
    1: pygame.transform.scale(pygame.image.load('SPRITES/TILES/1.png'), (TILE_SIZE, TILE_SIZE)),
    2: pygame.transform.scale(pygame.image.load('SPRITES/TILES/2.png'), (TILE_SIZE, TILE_SIZE)),
    3: pygame.transform.scale(pygame.image.load('SPRITES/TILES/3.png'), (TILE_SIZE, TILE_SIZE)),
    4: pygame.transform.scale(pygame.image.load('SPRITES/TILES/4.png'), (TILE_SIZE, TILE_SIZE)),
    5: pygame.transform.scale(pygame.image.load('SPRITES/TILES/5.png'), (TILE_SIZE, TILE_SIZE)),
    6: pygame.transform.scale(pygame.image.load('SPRITES/TILES/6.png'), (TILE_SIZE, TILE_SIZE)),
}

background = pygame.image.load('SPRITES/BACKGROUND/BG1.png')

class World():
    def __init__(self, screen):
        self.screen = screen
        self.world_data = self.load_world()
        self.tile_list = []
        self.grid = False

        # Tile images
        self.tile_0 = pygame.image.load('SPRITES/TILES/0.png')
        row_count = 0
        for row in self.world_data:
            col_count = 0
            for tile in row:
                if tile in tile_images:
                    img = tile_images[tile]
                    hitbox = img.get_rect()
                    hitbox.x = col_count * TILE_SIZE
                    hitbox.y = row_count * TILE_SIZE
                    tile_data = (img, hitbox)
                    self.tile_list.append(tile_data)
                col_count += 1
            row_count += 1

    def load_world(self):
        world_data = []
        with open('level_0.csv', newline='') as csvfile:
            for row in csv.reader(csvfile, delimiter=','):
                world_row = [int(cell) for cell in row]
                world_data.append(world_row)
        return world_data

    def draw(self):
        self.screen.fill(COLOR_BG)
        if not self.grid: self.screen.blit(background, (0,0))
        for tile in self.tile_list:
            if self.grid:
                self.screen.blit(self.tile_0, tile[1])
            else:                
                self.screen.blit(tile[0], tile[1])
    
        #     for line in range(0,50):
        #         pygame.draw.line(screen, WHITE, (0, line * TILE_SIZE), (SCREEN_WIDTH, line * TILE_SIZE))
        #         pygame.draw.line(screen, WHITE, (line * TILE_SIZE, 0), (line * TILE_SIZE, SCREEN_HEIGHT))