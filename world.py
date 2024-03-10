
# Libraries
import pygame
import os
import csv
from config import *

background = pygame.image.load('SPRITES/BACKGROUND/BG2.png')
tile_images = {}
for filename in os.listdir('SPRITES/TILES/'):
    if filename.endswith('.png') and filename != '0.png':
        tile_number = int(filename.split('.')[0])
        image_path = os.path.join('SPRITES/TILES/', filename)
        image = pygame.transform.scale(pygame.image.load(image_path), (TILE_SIZE, TILE_SIZE))
        tile_images[tile_number] = image

class World():
    def __init__(self, map_name):
        self.map_name = map_name
        self.world_data = self.load_world()
        self.tile_list = []

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
                    tile_data = (
                        img, # Sprite
                        hitbox, # Hitbox
                        self.solid(tile),                        
                        self.occupied(row_count+1, col_count), # Check if there is another tile below
                        self.border(row_count,col_count) # Check if its a border tile
                    )
                    self.tile_list.append(tile_data)
                col_count += 1
            row_count += 1

    def solid(self, tile):
        if tile in SOLID_TILES:
            return True
        else:
            return False

    def occupied(self, row, col):
        if self.world_data[row][col] != -1:
            return True
        else:
            return False
        
    def border(self, row, col):
        if (self.world_data[row][col-1] == -1 or self.world_data[row][col+1] == -1) and self.world_data[row-1][col] == -1:
            return True
        else:
            return False

    def load_world(self):
        world_data = []
        with open(self.map_name, newline='') as csvfile:
            for row in csv.reader(csvfile, delimiter=','):
                world_row = [int(cell) for cell in row]
                world_data.append(world_row)
        return world_data

    def draw(self, screen, grid):
        screen.fill(COLOR_BG)
        if not grid: screen.blit(background, (0,0))
        for tile in self.tile_list:
            if grid:
                if tile[2] == False: continue
                screen.blit(self.tile_0, tile[1])
                if tile[2]: pygame.draw.rect(screen, BLACK, tile[1], 1)
                if tile[4]: pygame.draw.rect(screen, BLUE, tile[1], 2)                
            else:                
                screen.blit(tile[0], tile[1])
    
        #     for line in range(0,50):
        #         pygame.draw.line(screen, WHITE, (0, line * TILE_SIZE), (SCREEN_WIDTH, line * TILE_SIZE))
        #         pygame.draw.line(screen, WHITE, (line * TILE_SIZE, 0), (line * TILE_SIZE, SCREEN_HEIGHT))