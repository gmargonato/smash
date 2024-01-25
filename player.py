
# Libraries
import pygame
import random
import time
import os
from config import *
from VFX import VFX 

# Auxiliar Variables
pygame.font.init()
font = pygame.font.SysFont('Arial Black', 30)
path = []

characters = {
    'CAP': {
        'scale'     : 0.75,
        'width'     : 75,
        'height'    : 95,
        'offset'    : (285,180),
    },  
}

class Player(pygame.sprite.Sprite):
    def __init__(self, screen, x, y, character, flip, ai):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.vfx = VFX(self.screen)
        self.ai = ai
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
        self.attacking = False
        self.modifier = False
        self.attack_type = 0
        self.cooldown = 0
        
        # Hitbox & Sprite Offset
        self.scale = characters[self.character]['scale']
        self.width = characters[self.character]['width'] * self.scale
        self.height = characters[self.character]['height'] * self.scale
        self.hitbox = pygame.Rect(x, y, self.width, self.height)
        self.offset = (characters[self.character]['offset'][0] * self.scale, characters[self.character]['offset'][1] * self.scale)

        # Sprites
        self.animations = {
            'idle'          : self.load_animation('idle'),
            'walk'          : self.load_animation('walk'),
            'crouch'        : self.load_animation('crouch'),
            'crouch_block'  : self.load_animation('crouch_block'),
            'block'         : self.load_animation('block'),
            'jump'          : self.load_animation('jump'),
            'mid_air'       : self.load_animation('mid_air'),
            'fall'          : self.load_animation('fall'),                        
            'atk_punch'     : self.load_animation('atk_punch'),
            'low_punch'     : self.load_animation('low_punch'),
            'high_punch'    : self.load_animation('high_punch'),
            'atk_kick'      : self.load_animation('atk_kick'),
            'low_kick'      : self.load_animation('low_kick'),
            'high_kick'     : self.load_animation('high_kick'),
        }

    def load_animation(self, name):
        animation_list = []
        path = f'SPRITES/{self.character}/{name.upper()}/'
        files = os.listdir(path)
        png_files = [file for file in files if file.endswith('.png')]
        png_files.sort(key=lambda x: int(x.split('.')[0]))    
        #print("PNG Files:", png_files)
        for png_file in png_files:
            full_path = os.path.join(path, png_file)
            try:
                img = pygame.image.load(full_path)
            except:
                img = pygame.image.load('/Users/gabrielmargonato/Documents/Python Scripts/smash/SPRITES/blank.png')
            img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
            img.set_colorkey((248,0,248))
            animation_list.append(img)
        #print(f"{name} List:",animation_list)
        return animation_list

    def update(self, tile_list, target):
        if self.ai:
            self.ai_input()
        else:
            self.get_input()
        self.combat(target)
        self.move(tile_list)
        self.animate()

    def ai_input(self):
        moves_list = ['n','m','b']
        if self.cooldown <= 0:
            
            self.blocking = False
            self.attacking = False
            self.jumping = False
            self.crouching = False
            
            selected_move = random.choice(moves_list)
            print(f"[AI] Timestamp: {time.time()} | Move: {selected_move}")
            self.cooldown = 500
            if selected_move == 'space':
                self.velocity_y = -GRAVITY*1.5
                self.jumping = True
            if not self.jumping:            
                if selected_move == 'b':
                    self.blocking = True            
                if selected_move == 's':
                    self.crouching = True                            
                if selected_move == 'n':                    
                    self.attacking = True
                    self.attack_type = 1
                if selected_move == 'm':
                    self.attacking = True
                    self.attack_type = 2      
        else:            
            self.cooldown -= 16
            
    def get_input(self):
        if self.attacking: return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.percentage += 5
        if keys[pygame.K_DOWN]:
            self.percentage -= 5
            
        # Walk
        if keys[pygame.K_d] or keys[pygame.K_a]:
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
        if keys[pygame.K_b]:
            self.blocking = True
        else:
            self.blocking = False 
        # Attack    
        if keys[pygame.K_n] or keys[pygame.K_m] and not self.attacking:
            self.attacking = True
            self.cooldown = 1000
            self.walking = False
        # Modifier    
        if keys[pygame.K_w]:
            self.modifier = True  
        else:
            self.modifier = False          
        # Jump
        if keys[pygame.K_SPACE] and not self.jumping and not self.in_air:        
            self.velocity_y = -GRAVITY*1.5
            self.jumping = True
        else:
            self.jumping = False

    def combat(self, target):
        
        # Getting hit by the other player
        if self.attacking and self.hitbox.colliderect(target.hitbox):
            if not target.blocking:
                target.percentage += 0.5
                if target.hitbox.x >= self.hitbox.x:
                    target.hitbox.x += 10 * target.percentage
                else:
                    target.hitbox.x -= 10 * target.percentage
            # else:
            #     print('Blocked!')

        if self.ai: return
        else: pass
        self.attack_type = 0

        # if self.cooldown > 0: 
        #     self.cooldown -= 16
        #     return

        # Calculates attack type
        keys = pygame.key.get_pressed()
        if keys[pygame.K_n]:
            self.attack_type = 1
            if self.crouching: self.attack_type = 3
            if self.modifier: self.attack_type = 5
        elif keys[pygame.K_m]:
            self.attack_type = 2 
            if self.crouching: self.attack_type = 4
            if self.modifier: self.attack_type = 6

    def move(self, tile_list):     

        global path
        SPEED = 10
        delta_x = 0
        delta_y = 0

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

        # Collision
        self.in_air = True
        for tile in tile_list:            
            #check for collision in x direction
            if tile[1].colliderect(self.hitbox.x + delta_x, self.hitbox.y, self.width, self.height):
                delta_x = 0
                self.momentum = 0
            #check for collision in y direction
            if tile[1].colliderect(self.hitbox.x, self.hitbox.y + delta_y, self.width, self.height):
                #check if below the ground i.e. jumping
                if self.velocity_y < 0:
                    delta_y = tile[1].bottom - self.hitbox.top
                    self.velocity_y = 0
                #check if above the ground i.e. falling
                if self.velocity_y >= 0:                    
                    delta_y = tile[1].top - self.hitbox.bottom
                    self.velocity_y = 0
                    self.in_air = False

        # Update plater coordinates
        self.hitbox.x += delta_x
        self.hitbox.y += delta_y

        if not self.ai:
            path.append((self.hitbox.x + self.hitbox.width // 2, self.hitbox.y + self.hitbox.height // 2))
            if len(path) > 50:
                path.pop(0)

        # Prevents falling from world
        if self.hitbox.bottom > SCREEN_HEIGHT:
            self.vfx.play_animation('ring_out', False, self.hitbox.centerx, self.hitbox.centery)
            self.hitbox.x = SCREEN_WIDTH/2-50
            self.hitbox.y = 0
            self.momentum = 0
            self.percentage = 0
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
                # Cooldown for attacking starts when the reaches the last frame
                if self.attacking: self.attacking = False
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
            elif self.crouching and not self.attacking:
                if self.blocking:
                    next_action = 'crouch_block'
                else:        
                    next_action = 'crouch'       
            elif self.attacking:
                if self.attack_type == 1:
                    next_action = 'atk_punch'
                if self.attack_type == 2:
                    next_action = 'atk_kick'
                if self.attack_type == 3:
                    next_action = 'low_punch'    
                if self.attack_type == 4:
                    next_action = 'low_kick'    
                if self.attack_type == 5:
                    next_action = 'high_punch'        
                if self.attack_type == 6:
                    next_action = 'high_kick'                   
            else:
                next_action = 'idle'            
        
        # Ensures the next action starts from frame 0
        if next_action != self.current_action:
            self.current_frame = 0
            self.current_action = next_action
        
    def draw(self):

        sprite = self.animations[self.current_action][self.current_frame]

        # Draw Character Portrait & Percentage
        self.draw_portrait()

        # Draw Player
        self.screen.blit(
            pygame.transform.flip(sprite, self.flip, False), 
            (self.hitbox.x - self.offset[0], self.hitbox.y - self.offset[1])
        )      

        # Draw Grid
        if self.grid:
            if self.ai:
                pygame.draw.rect(self.screen, RED, self.hitbox, 1)
            else:
                pygame.draw.rect(self.screen, WHITE, self.hitbox, 1)
                print(f"Pos: {self.hitbox.center}| Action: {self.current_action} | Attack: (A: {self.attacking}, T: {self.attack_type}, C: {self.cooldown}) | Frame: {self.current_frame} | Flip: {self.flip} | Velocity (Y): {self.velocity_y}")            
                for i in range(1, len(path)):
                    pygame.draw.line(self.screen, WHITE, path[i - 1], path[i])
            
    def draw_portrait(self):
        portrait_width = 100
        portrait_height = 100

        # Portrait
        #self.screen.blit(pygame.transform.scale(self.portrait, (portrait_width, portrait_height)), (SCREEN_WIDTH // 2 - portrait_width // 2, SCREEN_HEIGHT - 100))

        # Percentage
        percentage_text = font.render(f"{str('%.2f' % self.percentage)}%", True, BLACK)
        if not self.ai:
            self.screen.blit(percentage_text, (SCREEN_WIDTH/2-100, SCREEN_HEIGHT - 100))
        else:
            self.screen.blit(percentage_text, (SCREEN_WIDTH/2+100, SCREEN_HEIGHT - 100))
