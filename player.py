
# Libraries
import pygame
import random
import math
import os
from config import *

# Auxiliar Variables
pygame.font.init()
font = pygame.font.SysFont('Arial Black', 20)
path = []

characters = {
    'CAP1': {
        'speed'     : 10,
        'scale'     : 0.75,
        'width'     : 45,
        'height'    : 80,
        'projectile':'cap_shield',
    },
    'CAP2': {
        'speed'     : 10,
        'scale'     : 0.75,
        'width'     : 45,
        'height'    : 80,        
        'projectile':None,
    },
    'RYU': {
        'speed'     : 10,
        'scale'     : 0.85,
        'width'     : 45,
        'height'    : 80,
        'projectile':'hadouken',
    },
    'SPIDER': {
        'speed'     : 10,
        'scale'     : 0.8,
        'width'     : 45,
        'height'    : 80,
        'offset'    : 20,
        'projectile':'web',
    },
    'VENOM': {
        'speed'     : 10,
        'scale'     : 0.8,
        'width'     : 50,
        'height'    : 80,
        'offset'    : 20,
        'projectile':'web',
    },
}

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character, flip, controller, lives, percentage):
        pygame.sprite.Sprite.__init__(self)
        self.controller = controller # P1, P2 or AI
        self.lives = lives
        self.percentage = percentage
        self.character = character
        self.events = []
        self.current_action = 'idle'
        self.current_frame = 0       
        self.last_frame_update = 0
        self.velocity_y = 0
        self.momentum = 0
        self.in_air = True
        self.flip = flip
        self.walking = False
        self.crouching = False
        self.jumping = False        
        self.blocking = False
        self.hit = False
        self.stun_cooldown = 0
        self.start_attack = None
        self.currently_attacking = False        
        self.attack_type = None
        self.next_attack_window = 0        
        self.shoot_cooldown = 0
        
        # Sprites, Hitbox & Offset
        self.scale      = characters[self.character]['scale']
        self.shoot_type = characters[self.character]['projectile']
        self.speed      = characters[self.character]['speed']
        self.animations = {
            'idle'          : self.load_animation('IDLE'),
            'walk'          : self.load_animation('WALK'),
            'crouch'        : self.load_animation('CROUCH'),
            'block'         : self.load_animation('BLOCK'),
            'crouch_block'  : self.load_animation('CROUCH_BLOCK'),
            'jump'          : self.load_animation('JUMP'),
            'mid_air'       : self.load_animation('MID_AIR'),
            'fall'          : self.load_animation('FALL'),
            'NP1'           : self.load_animation('NORMAL_PUNCH'),
            'LP1'           : self.load_animation('LOW_PUNCH'),
            'NK1'           : self.load_animation('NORMAL_KICK'),
            'LK1'           : self.load_animation('LOW_KICK'),            
            'NS1'            : self.load_animation('NORMAL_SHOOT'),
        }
        self.width      = characters[self.character]['width']
        self.height     = characters[self.character]['height']        
        self.image      = self.animations[self.current_action][self.current_frame]        
        self.rect       = pygame.Rect(x, y, self.width, self.height) 
        self.mask       = pygame.mask.from_surface(self.image)
        
        # Offsets
        try:
            self.base_offset_x = characters[self.character]['offset'] * (1 if self.flip else -1)
        except:
            self.base_offset_x = 0

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
        if self.controller == 'AI':
            self.ai_input(tile_list, target)
        else:
            self.get_input()
        self.combat(target)
        self.move(tile_list, target)
        self.animate()

    def ai_input(self, tile_list, target):

        # self.walking = False
        # if target.rect.bottom == self.rect.bottom: # If on the same platform as the player            
            # self.walking = True
        self.flip = target.rect.x < self.rect.x
        # else:
        #     for tile in tile_list:            
        #         if tile[1].colliderect(self.rect.move(0, 1)) and tile[4] and tile[2]: # If on a border, flip direction
        #             self.flip = not self.flip  
        #             break                  
                    
        keys = pygame.key.get_pressed()
        # if keys[pygame.K_n] or keys[pygame.K_m]:            
        #     chance = random.randint(1, 10)
        #     if chance == 1: self.blocking = not self.blocking
        if keys[pygame.K_h] and self.shoot_cooldown <= 0:
            self.shoot_cooldown = 100            
            self.events.append(('projectile', (self.rect.centerx, self.rect.centery)))    
                
    def get_input(self):

        # Do not get inputs if the player is stunned
        if self.stun_cooldown > 0: return

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
        if keys[pygame.K_w] and not self.jumping and not self.in_air and not self.crouching and not self.currently_attacking:        
            self.velocity_y = -GRAVITY*1.5
            self.jumping = True
        else:
            self.jumping = False
        # Attack
        if (keys[pygame.K_n] or keys[pygame.K_m]) and not self.currently_attacking and self.next_attack_window <= 0 and not self.in_air: 
            if (keys[pygame.K_n] and keys[pygame.K_m]) and self.shoot_cooldown <= 0 and self.shoot_type != None:
                self.start_attack = 'shooting'
            elif keys[pygame.K_n]:
                self.start_attack = 'punch'
            else:
                self.start_attack = 'kick'
        
    def combat(self, target):

        self.stun_cooldown      = max(0, self.stun_cooldown - 10)
        self.shoot_cooldown     = max(0, self.shoot_cooldown - 10)
        self.next_attack_window = max(0, self.next_attack_window - 10)
        
        # Starting an attack
        if self.start_attack != None:
            self.currently_attacking = True
            self.walking = False
            self.blocking = False
            # set attack type
            if self.start_attack == 'shooting':
                self.shoot_cooldown = 1300
                self.attack_type = 'NS1'   
                self.events.append(('projectile', (self.rect.centerx, self.rect.centery)))                
            elif self.start_attack == 'punch':
                self.next_attack_window = 100
                if self.crouching:  self.attack_type = 'LP1'
                else:               self.attack_type = 'NP1'
            else: #Kick
                self.next_attack_window = 100
                if self.crouching:  self.attack_type = 'LK1' 
                else:               self.attack_type = 'NK1'
            self.start_attack = None 
        
        # Collision system between one player (self) and another (target)        
        if self.currently_attacking:
            if self.get_collision(target):                            
                if (
                    (self.attack_type[0] == 'N' and not target.blocking) or
                    (self.attack_type[0] == 'L' and not (target.blocking and target.crouching)) or
                    (target.currently_attacking and target.current_frame < self.current_frame)
                ):    
                    # self.events.append(('hit', (self.rect.left if self.flip else self.rect.right, self.rect.y)))  
                    target.percentage = min(target.percentage + 0.05, 100)
                    rounded_percentage = math.floor(target.percentage) # Rounds the percentge down to the nearest integer
                    target.velocity_y = - (5+rounded_percentage%10)
                    # Push mechanic
                    roll = random.randint(rounded_percentage, 100)
                    target.momentum = 50 if roll == rounded_percentage else 5 * (1 if self.rect.x < target.rect.x else -1)

    def get_collision(self, target):
        if self.rect.centerx < target.rect.centerx:
            overlap = self.mask.overlap(target.mask, (target.rect.x - self.rect.x , target.rect.y - self.rect.y))
        else:
            overlap = self.mask.overlap(target.mask, (self.rect.x - target.rect.x, target.rect.y - self.rect.y))            
        return overlap is not None        
        
    def move(self, tile_list, target):     

        global path
        delta_x = 0
        delta_y = 0

        # Walking
        if not self.in_air:
            if self.walking: delta_x = -self.speed if self.flip else self.speed
            self.momentum = delta_x
        else:
            if self.momentum > 0: self.momentum -= 0.125
            if self.momentum < 0: self.momentum += 0.125
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
            if tile[1].colliderect(self.rect.move(delta_x, 0)):
                delta_x = 0
                self.momentum = 0
            #check for collision in y direction
            if tile[1].colliderect(self.rect.move(0, delta_y)):
                # jumping
                if self.velocity_y < 0:
                    delta_y = tile[1].top - (self.rect.bottom + 3)
                    self.velocity_y = 0
                # falling
                elif self.velocity_y >= 0:
                    delta_y = tile[1].top - self.rect.bottom
                    self.velocity_y = 0                    
                    self.in_air = False                    
                    # Jumping while crouching makes it fall through the platform
                    if (self.crouching and pygame.key.get_pressed()[pygame.K_w] and not tile[3]) or(self.controller == 'AI' and self.rect.y <= 200):
                        self.in_air = True
                        self.rect.top = tile[1].bottom

        # Update player coordinates
        self.rect.x += delta_x
        self.rect.y += delta_y

        if self.controller != 'AI':
            path.append((self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2))
            if len(path) > 50:
                path.pop(0)

        # If falls from ring
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.events.append(('ring_out', (self.rect.centerx, SCREEN_HEIGHT)))
            self.rect.x = SCREEN_WIDTH/2-50
            self.rect.y = 0
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

        # Update Image
        self.image  = pygame.transform.flip(self.animations[self.current_action][self.current_frame], self.flip, False)
        self.mask   = pygame.mask.from_surface(self.image)
        # Calculate Offset
        if not self.flip:
            self.offset_x = self.base_offset_x
        else:
            self.offset_x = - self.base_offset_x + self.rect.width - self.image.get_width()

    def draw(self, screen, grid):        
        # Draw Percentage
        percentage_text = font.render(f"{str('%.2f' % self.percentage)}%", True, BLACK)
        lives_text      = font.render(f"Lives: {str(self.lives)}", True, BLACK)
        if self.controller == 'P1':
            screen.blit(percentage_text, (SCREEN_WIDTH/2-200, SCREEN_HEIGHT - 100))
            screen.blit(lives_text, (SCREEN_WIDTH/2-200, SCREEN_HEIGHT - 50))
        else: # Player 2 or AI
            screen.blit(percentage_text, (SCREEN_WIDTH/2+100, SCREEN_HEIGHT - 100))
            screen.blit(lives_text, (SCREEN_WIDTH/2+100, SCREEN_HEIGHT - 50))

        # Draw Grid
        if grid:
        
            # Print Hitbox
            pygame.draw.rect(screen, RED if self.controller == "AI" else GREEN, self.rect, 1)
        
            for i in range(1, len(path)):
                pygame.draw.line(screen, WHITE, path[i - 1], path[i])
            
            # Draw Mask
            screen.blit(self.mask.to_surface(unsetcolor=(0,0,0,0), setcolor=(255,255,255,255)), (self.rect.x + self.offset_x, self.rect.y - self.image.get_height() + self.rect.height + 9))                
        
        # Draw Player if not stunned
        if self.stun_cooldown <= 0 :                
            screen.blit(self.image, (self.rect.x + self.offset_x, self.rect.y - self.image.get_height() + self.rect.height + 10))
        
        # Debug Info
        print(f"""
                Pos: {self.rect.center} | X-Velocity: {int(self.momentum)} | Y-Velocity: {int(self.velocity_y)}
                Animation: ({self.current_action},{self.current_frame})
                Hit: {self.hit} | Stun: {self.stun_cooldown}
                Attack: ({self.currently_attacking},{self.attack_type},{self.next_attack_window})
                Shoot: {self.shoot_cooldown} 
        """)
        
            