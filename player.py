
# Libraries
import pygame
import random
import time
import os
from config import *

# Auxiliar Variables
pygame.font.init()
font = pygame.font.SysFont('Arial Black', 20)
path = []

characters = {
    'CAP_SHIELD': {
        'scale'     : 0.75,
        'width'     : 75,
        'height'    : 95,
        'offset'    : (10,10),
        'projectile':'boomerang',
    },
}

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character, flip, type):
        pygame.sprite.Sprite.__init__(self)
        self.ai = True if type == 'AI' else False
        self.lives = 3
        self.percentage = 0
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
        self.start_attack = None
        self.currently_attacking = False
        self.attack_cycle = 1
        self.attack_type = None
        self.attack_cooldown = 0
        self.shoot_type = characters[self.character]['projectile']
        self.shoot = False
        self.shoot_cooldown = 0
        
        # Hitbox & Sprite Offset
        self.scale = characters[self.character]['scale']
        self.width = characters[self.character]['width'] * self.scale
        self.height = characters[self.character]['height'] * self.scale
        self.offset = (characters[self.character]['offset'][0] * self.scale, characters[self.character]['offset'][1] * self.scale)        
        self.hitbox = pygame.Rect(x, y, self.width, self.height)

        # Sprites
        self.animations = {
            'idle'          : self.load_animation('IDLE'),
            'walk'          : self.load_animation('WALK'),
            'crouch'        : self.load_animation('CROUCH'),
            'block'         : self.load_animation('BLOCK'),
            'crouch_block'  : self.load_animation('CROUCH_BLOCK'),
            'jump'          : self.load_animation('JUMP'),
            'mid_air'       : self.load_animation('MID_AIR'),
            'fall'          : self.load_animation('FALL'),
            'NP1'           : self.load_animation('NORMAL_PUNCH_1'),
            'NP2'           : self.load_animation('NORMAL_PUNCH_2'),
            'LP1'           : self.load_animation('LOW_PUNCH_1'),
            'LP2'           : self.load_animation('LOW_PUNCH_2'),
            'NK1'           : self.load_animation('NORMAL_KICK_1'),
            'NK2'           : self.load_animation('NORMAL_KICK_2'),
            'NK3'           : self.load_animation('NORMAL_KICK_3'),
            'LK1'           : self.load_animation('LOW_KICK_1'),
            'LK2'           : self.load_animation('LOW_KICK_2'),
            'NS1'            : self.load_animation('NORMAL_SHOOT'),
        }

    def load_animation(self, name):
        animation_list = []
        path = f'SPRITES/{self.character}/{name}/'
        files = os.listdir(path)
        png_files = [file for file in files if file.endswith('.png')]
        png_files.sort(key=lambda x: int(x.split('.')[0]))    
        for png_file in png_files:
            full_path = os.path.join(path, png_file)
            img = pygame.image.load(full_path)#.convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
            #img.set_colorkey((248,0,248))
            animation_list.append(img)
        return animation_list

    def update(self, tile_list, target):
        if self.ai:
            self.ai_input(target)
        else:
            self.get_input()
        self.combat(target)
        self.move(tile_list)
        self.animate()

    def ai_input(self, target):
        #self.blocking = True
        if target.hitbox.x < self.hitbox.x:
            self.flip = True        
        else:
            self.flip = False     
        if self.hitbox.y <= 200: self.hitbox.y = 316
            
    def get_input(self):

        keys = pygame.key.get_pressed()

        # Walk
        if (keys[pygame.K_d] or keys[pygame.K_a]) and not self.currently_attacking and not self.blocking:
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
        if keys[pygame.K_b] and not self.currently_attacking:
            self.blocking = True
            self.walking = False
        else:
            self.blocking = False 
        # Jump
        if keys[pygame.K_w] and not self.jumping and not self.in_air and not self.crouching:        
            self.velocity_y = -GRAVITY*1.5
            self.jumping = True
        else:
            self.jumping = False
        # Attack
        if (keys[pygame.K_n] or keys[pygame.K_m]) and not self.currently_attacking and not self.in_air: 
            if (keys[pygame.K_n] and keys[pygame.K_m]) and self.shoot_cooldown <= 0:
                self.start_attack = 'shooting'
            elif keys[pygame.K_n]:
                self.start_attack = 'punch'
            else:
                self.start_attack = 'kick'
        
    def combat(self, target):

        self.shoot_cooldown  = max(0, self.shoot_cooldown - 10)
        self.attack_cooldown = max(0, self.attack_cooldown - 10)
        
        # Cycle through attacks
        if self.attack_cooldown <= 0:
            self.attack_cycle = 1
        else:            
            self.attack_cycle = 2

        # Starting an attack
        if self.start_attack != None:
            self.currently_attacking = True
            self.walking = False
            self.blocking = False
            # set attack type
            if self.start_attack == 'shooting':
                self.shoot_cooldown = 1300
                self.attack_type = 'NS1'                    
                self.shoot = True
            elif self.start_attack == 'punch':
                self.attack_cooldown = 150
                if self.crouching:  self.attack_type = f'LP{self.attack_cycle}'
                else:               self.attack_type = f'NP{self.attack_cycle}'
            else: #Kick
                self.attack_cooldown = 150
                if self.crouching:  self.attack_type = f'LK{self.attack_cycle}' 
                else:               self.attack_type = f'NK{self.attack_cycle}'
            self.start_attack = None 
        
        # Collision with the other player
        elif self.currently_attacking == True:
            if self.hitbox.colliderect(target.hitbox) and not target.blocking:
                target.percentage += 0.5
                if target.hitbox.x >= self.hitbox.x:
                    target.hitbox.x += 10 * target.percentage
                else:
                    target.hitbox.x -= 10 * target.percentage

    def move(self, tile_list):     

        global path
        SPEED = 10
        delta_x = 0
        delta_y = 0

        # Walking
        if not self.in_air:
            if self.walking: delta_x = -SPEED if self.flip else SPEED
            self.momentum = delta_x
        else:
            if self.momentum > 0: self.momentum -= 0.15
            if self.momentum < 0: self.momentum += 0.15
            delta_x = self.momentum

        # Gravity
        self.velocity_y += 1
        if self.velocity_y > GRAVITY:
            self.velocity_y = GRAVITY
        delta_y += self.velocity_y

        # Collision with Tiles
        self.in_air = True
        for tile in tile_list:
            # check if solid tile
            if tile[2] == False: continue
            # check for collision in x direction
            if tile[1].colliderect(self.hitbox.x + delta_x, self.hitbox.y, self.width, self.height):
                delta_x = 0
                self.momentum = 0
            #check for collision in y direction
            if tile[1].colliderect(self.hitbox.x, self.hitbox.y + delta_y, self.width, self.height):
                # jumping
                if self.velocity_y < 0:
                    # delta_y = tile[1].bottom - self.hitbox.top
                    delta_y = tile[1].top - (self.hitbox.bottom + 3)
                    self.velocity_y = 0
                # falling
                elif self.velocity_y >= 0:
                    delta_y = tile[1].top - self.hitbox.bottom
                    self.velocity_y = 0
                    self.in_air = False
                    # Jumping while crouching makes it fall through the platform
                    if self.crouching and pygame.key.get_pressed()[pygame.K_w] and not tile[3]:
                        self.in_air = True
                        self.hitbox.top = tile[1].bottom

        # Update player coordinates
        self.hitbox.x += delta_x
        self.hitbox.y += delta_y

        if not self.ai:
            path.append((self.hitbox.x + self.hitbox.width // 2, self.hitbox.y + self.hitbox.height // 2))
            if len(path) > 50:
                path.pop(0)

        # Prevents falling from world
        if self.hitbox.bottom > SCREEN_HEIGHT:
            self.hitbox.x = SCREEN_WIDTH/2-50
            self.hitbox.y = 0
            self.momentum = 0
            self.percentage = 0
            self.lives = self.lives - 1
            path = []
            
    def animate(self):

        num_frames = len(self.animations[self.current_action])
        last_frame = num_frames - 1

        FPS = 50
        if num_frames == 2: FPS *= 4
        
        # Disassociate animation interval from game's FPS
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_update < FPS:
            return
        else: 
            self.last_frame_update = current_time

        # Animation Loop
        if num_frames == 1:
            self.current_frame = 0
        else:
            if self.current_frame < last_frame: # Keep looping while state is true
                self.current_frame += 1                
            else: # If it is the last frame of animation                
                self.current_frame = 0
                self.currently_attacking = False
                self.attack_type = None
        next_action = self.current_action

        if self.in_air:
            if self.velocity_y <= -3:
                next_action = 'jump'
            elif -2 <= self.velocity_y < 7:                
                next_action = 'mid_air'
            else:
                next_action = 'fall'
        else:
            if self.walking:
                next_action = 'walk'
            elif self.blocking and not self.crouching:
                next_action = 'block'
            elif self.crouching and not self.currently_attacking:
                if self.blocking:
                    next_action = 'crouch_block'
                else:        
                    next_action = 'crouch'       
            elif self.currently_attacking:
                next_action = self.attack_type                
            else:
                next_action = 'idle'            
        
        # Ensures the next action starts from frame 0
        if next_action != self.current_action:
            self.current_frame = 0
            self.current_action = next_action

        # Update hitbox
        sprite = self.animations[self.current_action][self.current_frame]
        self.hitbox = pygame.Rect(self.hitbox.x, self.hitbox.y, sprite.get_width()*0.80, self.height)

    def draw(self, screen):
        sprite = self.animations[self.current_action][self.current_frame]
        
        # Draw Percentage
        percentage_text = font.render(f"{str('%.2f' % self.percentage)}%", True, BLACK)
        lives_text      = font.render(f"Lives: {str(self.lives)}", True, BLACK)
        if not self.ai: #Player
            screen.blit(percentage_text, (SCREEN_WIDTH/2-200, SCREEN_HEIGHT - 100))
            screen.blit(lives_text, (SCREEN_WIDTH/2-200, SCREEN_HEIGHT - 50))
        else: # AI
            screen.blit(percentage_text, (SCREEN_WIDTH/2+100, SCREEN_HEIGHT - 100))
            screen.blit(lives_text, (SCREEN_WIDTH/2+100, SCREEN_HEIGHT - 50))

        # Draw Grid
        if self.grid:
            # Mask
            # sprite_mask = pygame.mask.from_surface(sprite)
            # mask_surface = pygame.transform.flip(sprite_mask.to_surface(unsetcolor=(0, 0, 0, 0)), self.flip, False)
            # screen.blit(mask_surface, (self.hitbox.x - self.offset[0], self.hitbox.y - self.offset[1]))

            if self.ai:
                pygame.draw.rect(screen, RED, self.hitbox, 1)
            else:
                pygame.draw.rect(screen, GREEN, self.hitbox, 1)
                print(f"""
                      Pos: {self.hitbox.center} | Y-Velocity: {self.velocity_y}
                      Animation: ({self.current_action},{self.current_frame})
                      Attack: ({self.currently_attacking},{self.attack_type},{self.attack_cooldown})
                      Shoot: {self.shoot},{self.shoot_cooldown}  
                """)
                for i in range(1, len(path)):
                    pygame.draw.line(screen, WHITE, path[i - 1], path[i])
        # else:
        # Draw Player
        screen.blit(pygame.transform.flip(sprite, self.flip, False),  (self.hitbox.x - self.offset[0]*2, self.hitbox.y - self.offset[1]))
