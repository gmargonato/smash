
import pygame
import os
from config import *

font = pygame.font.SysFont('Arial Black', 15)

projectile_list = {
    'boomerang' : "/Users/gabrielmargonato/Documents/Python Scripts/smash/SPRITES/CAP1/PROJECTILE",
    'hadouken'  : "/Users/gabrielmargonato/Documents/Python Scripts/smash/SPRITES/RYU/PROJECTILE",
}

class Projectile(pygame.sprite.Sprite):
    def __init__(self, owner, x, y, direction, type):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 15
        self.owner = owner
        self.direction = direction        
        self.type = type
        self.frame_index = 0
        self.images = self.load_images()
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x + 100, y + 30)
        self.bounce = 0

    def load_images(self):
        images = []
        folder_path = projectile_list[self.type]
        for file_name in sorted(os.listdir(folder_path)):
            if file_name.endswith('.png'):
                image = pygame.image.load(os.path.join(folder_path, file_name))#.convert_alpha()
                images.append(image)
        return images

    def update(self):

        # Update projectile animation
        self.frame_index += 1
        if self.frame_index >= len(self.images):
            self.frame_index = 0
        self.image = self.images[self.frame_index]

        # Update projectile position
        self.rect.x += (self.speed * self.direction)
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            if self.type == "boomerang":
                self.direction *= -1
                self.bounce += 1
            else:
                self.kill()

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, True if self.direction < 0 else False, False), self.rect)
        text = font.render(self.owner, True, GREEN if self.owner == 'P1' else RED)
        screen.blit(text, (self.rect.centerx-10, self.rect.y-20))
