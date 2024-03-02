
import pygame
from config import *

projectile_list = {
    'cap_shield'    : "/Users/gabrielmargonato/Documents/Python Scripts/smash/SPRITES/CAP_SHIELD/SHIELD.png",
    'hadouken'      : "",
}

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, type):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(projectile_list['cap_shield']).convert_alpha()
        self.speed = 15
        self.direction = direction
        self.rect = self.image.get_rect()
        self.rect.center = (x,y+20)
        self.type = type
        self.grid = False
        self.bounce_count = 0

    def update(self):
        self.rect.x += (self.speed * self.direction)
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            if self.type == "boomerang" and self.bounce_count < 1:
                self.direction *= -1
                self.bounce_count += 1
            else:
                self.kill()
