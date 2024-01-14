
# Libraries
import pygame
import random
import time
import os
import csv
from config import *

class World():
    def __init__(self):
        self.world_data = self.load_world()
        self.tile_list = []
        self.grid = False

        # Tile images
        tile_1 = pygame.image.load('SPRITES/TILES/1.png')

        row_count = 0
        for row in self.world_data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(tile_1, (TILE_SIZE, TILE_SIZE))
                    hitbox = img.get_rect()
                    hitbox.x = col_count * TILE_SIZE
                    hitbox.y = row_count * TILE_SIZE
                    tile = (img, hitbox)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1 

    def load_world(self):
        world_data = []
        with open('level_0.csv', newline='') as csvfile:
            for row in csv.reader(csvfile, delimiter=','):
                world_row = [int(cell) for cell in row]
                world_data.append(world_row)
        return world_data

    def draw(self, screen):
        screen.fill(COLOR_BG)
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
        # if self.grid:
        #     for line in range(0,50):
        #         pygame.draw.line(screen, WHITE, (0, line * TILE_SIZE), (SCREEN_WIDTH, line * TILE_SIZE))
        #         pygame.draw.line(screen, WHITE, (line * TILE_SIZE, 0), (line * TILE_SIZE, SCREEN_HEIGHT))