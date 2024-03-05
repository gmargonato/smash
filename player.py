
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
        'height'    : 80,
        'offset'    : (20,0),
        'projectile':'boomerang',
    },
    'CAP2': {
        'speed'     : 10,
        'scale'     : 0.75,
        'height'    : 80,
        'offset'    : (20,0),
        'projectile':None,
    },
    'RYU': {
        'speed'     : 10,
        'scale'     : 0.85,
        'height'    : 80,
        'offset'    : (20,15),
        'projectile':'hadouken',
    },
}

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character, flip, controller, lives, percentage):
        pygame.sprite.Sprite.__init__(self)
        self.controller = controller # P1, P2 or AI
        self.lives = lives
        self.percentage = percentage
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
        self.attack_type = None
        self.next_attack_window = 0        
        self.shoot = False
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
        self.sprite     = self.animations[self.current_action][self.current_frame]
        self.width      = self.sprite.get_width() 
        self.height     = characters[self.character]['height']
        self.offset     = (characters[self.character]['offset'][0], characters[self.character]['offset'][1])        
        self.hitbox     = pygame.Rect(x, y, self.width, self.height)

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
            self.ai_input(target)
        else:
            self.get_input()
        self.combat(target)
        self.move(tile_list, target)
        self.animate()

    def ai_input(self, target):
        if target.hitbox.x < self.hitbox.x:
            self.flip = True        
        else:
            self.flip = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_j]:
            self.blocking = True
        else:
            self.blocking = False

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
        if (keys[pygame.K_n] or keys[pygame.K_m]) and not self.currently_attacking and self.next_attack_window <= 0 and not self.in_air: 
            if (keys[pygame.K_n] and keys[pygame.K_m]) and self.shoot_cooldown <= 0 and self.shoot_type != None:
                self.start_attack = 'shooting'
            elif keys[pygame.K_n]:
                self.start_attack = 'punch'
            else:
                self.start_attack = 'kick'
        
    def combat(self, target):

        self.shoot_cooldown  = max(0, self.shoot_cooldown - 10)
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
                self.shoot = True            
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


        # TO-DO: PIXEL-PERFECT COLLISION USING MASKS
        # sprite_mask = pygame.mask.from_surface(sprite)
        # mask_surface = pygame.transform.flip(sprite_mask.to_surface(unsetcolor=(0, 0, 0, 0)), self.flip, False)
        # screen.blit(mask_surface, (self.hitbox.x - self.offset[0], self.hitbox.y - self.offset[1]))
        
        if self.currently_attacking and self.hitbox.colliderect(target.hitbox):
            if (
                (self.attack_type[0] == 'N' and not target.blocking) or
                (self.attack_type[0] == 'L' and not (target.blocking and target.crouching)) or
                (target.currently_attacking and target.current_frame < self.current_frame)
            ):
                target.percentage = min(target.percentage + 0.05, 100)
                target.velocity_y = -GRAVITY/2
                # Random push mechanic
                roll = random.randint(math.floor(target.percentage), 100)
                target.momentum = 50 if roll == math.floor(target.percentage) else 5 * (1 if self.hitbox.x < target.hitbox.x else -1)                

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
            if tile[1].colliderect(self.hitbox.move(delta_x, 0)):
                delta_x = 0
                self.momentum = 0
            #check for collision in y direction
            if tile[1].colliderect(self.hitbox.move(0, delta_y)):
                # jumping
                if self.velocity_y < 0:
                    delta_y = tile[1].top - (self.hitbox.bottom + 3)
                    self.velocity_y = 0
                # falling
                elif self.velocity_y >= 0:
                    delta_y = tile[1].top - self.hitbox.bottom
                    self.velocity_y = 0                    
                    self.in_air = False
                    # Jumping while crouching makes it fall through the platform
                    if (self.crouching and pygame.key.get_pressed()[pygame.K_w] and not tile[3]) or(self.controller == 'AI' and self.hitbox.y <= 200):
                        self.in_air = True
                        self.hitbox.top = tile[1].bottom

        # Collision with Players
        # if self.hitbox.move(delta_x, 0).colliderect(target.hitbox):
        #     delta_x = 0

        # Update player coordinates
        self.hitbox.x += delta_x
        self.hitbox.y += delta_y

        if self.controller != 'AI':
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
        self.hitbox = pygame.Rect(self.hitbox.x, self.hitbox.y, self.sprite.get_width() * (1 if self.currently_attacking else 0.5), self.height)

    def draw(self, screen):
        sprite = self.animations[self.current_action][self.current_frame]
        
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
        if self.grid:

            if self.controller == 'AI':
                pygame.draw.rect(screen, RED, self.hitbox, 1)
            else:
                pygame.draw.rect(screen, GREEN, self.hitbox, 1)
                print(f"""
                      Pos: {self.hitbox.center} | Y-Velocity: {self.velocity_y} | Momentum: {self.momentum}
                      Animation: ({self.current_action},{self.current_frame})
                      Attack: ({self.currently_attacking},{self.attack_type},{self.next_attack_window})
                      Shoot: {self.shoot},{self.shoot_cooldown}  
                """)
                for i in range(1, len(path)):
                    pygame.draw.line(screen, WHITE, path[i - 1], path[i])
        # else:
        # Draw Player
        screen.blit(pygame.transform.flip(sprite, self.flip, False),  (self.hitbox.x - self.offset[0], self.hitbox.y - self.offset[1]))
