
# Libraries
import pygame
import random
import sys
from config import *

class Snow:
    def __init__(self, screen):
        self.screen = screen
        self.list_of_particles = []

    def generate_one_particle(self):
        starting_pos = [random.randint(-100, SCREEN_WIDTH), 0]
        move_pos = [random.randint(0, 20) / 10 - 1, 2]
        radius = random.randint(2, 4)
        return [starting_pos, move_pos, radius]

    def snow_flakes_generator(self):
        self.list_of_particles.append(self.generate_one_particle())

        # Every particle  moves... if list_of_particles[2] (the radius) is >= than 0 it is removed
        for particle in self.list_of_particles[:]:
            
            # parameters for new position (aka speed) and shrinking
            direction = particle[1][0]      # random direction fixed
            velocity = particle[1][1]  # get the next position on the y axes
            gravity = 0.01            # how fast it falls
            melting = 0.005         # how fast it shrinks

            # the starting point changes going right or left
            particle[0][0] += direction+random.randint(0,2) # increase the x position of an angle (to the right or left)
            particle[0][1] +=  velocity # the y movement going down speed fixed 2
                                            # but it is increased of 0.01 down here, so it goes down at the same speed
            particle[2] -= melting # the snowflake shriks
            particle[1][1] += gravity # * random.randint(-3, 6) # increase down speed a bit
            if particle[2] <= 0: # when the radius is 0 it is removed, so we do not see it anymore and it's not in the memory
                self.list_of_particles.remove(particle)

        # draws a circle on the screen white, at x y corrds and with a ray of particle[2]
        for particle in self.list_of_particles:
            pos = particle[0][0]
            speed = particle[0][1]
            radius = particle[2]
            # circle: surface, color, pos, radius
            pygame.draw.circle(
            	self.screen,
            	(255, 244, 255), # color
            	(
            		round(pos), # Pos x, y
            		round(speed)), # direction / speed
            		round(radius)) # radius

