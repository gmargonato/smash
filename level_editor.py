import pygame
import csv
import pickle
from config import *

pygame.init()

clock = pygame.time.Clock()
FPS = 60

#game window
LOWER_MARGIN = 125
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')

#define game variables
ROWS = 20
MAX_COLS = 40
TILE_TYPES = 2
level = 0
page = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1
show_grid = True

# TILE-BUTTON CLASS
class TileButton():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		pos = pygame.mouse.get_pos()
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

# SIMPLE-BUTTON CLASS
class SimpleButton:
    def __init__(self, display_text, x, y):
        self.display_text = display_text
        self.rect = pygame.Rect(x, y, 50, 50)
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)
        text_surface = self.font.render(self.display_text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect.topleft)
prev_button = SimpleButton("<", SCREEN_WIDTH + SIDE_MARGIN/4, SCREEN_HEIGHT + LOWER_MARGIN/3)
next_button = SimpleButton(">", SCREEN_WIDTH + SIDE_MARGIN/2, SCREEN_HEIGHT + LOWER_MARGIN/3)

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'SPRITES/TILES/{x}.png').convert_alpha()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)

#define colours
GRAY 	= (93, 93, 93)
WHITE 	= (255, 255, 255)
BLACK 	= (0,0,0)
RED 	= (200, 25, 25)

#define font
font = pygame.font.SysFont('Futura', 15)

#create empty tile list
world_data = []
for row in range(ROWS):
	r = [-1] * MAX_COLS
	world_data.append(r)

#create ground
for tile in range(0, MAX_COLS):
	world_data[ROWS - 1][tile] = -1

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	text = font.render(text, True, text_col)
	screen.blit(text, (x, y))

#create function for drawing background
def draw_bg():
	screen.fill(GRAY)

#function for drawing the world tiles
def draw_world():
	for y, row in enumerate(world_data):
		for x, tile in enumerate(row):
			if tile >= 0:
				screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))

def draw_grid():
	# vertical lines
	for c in range(MAX_COLS + 1):
		# pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
		pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, min(SCREEN_HEIGHT, (ROWS + 1) * TILE_SIZE)))

	# horizontal lines
	for c in range(ROWS + 1):
		pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))
		# Draw row numbers
		number_text = font.render(str(c), True, WHITE)
		screen.blit(number_text, (0, c * TILE_SIZE + 0.2*TILE_SIZE))

#make a tile-button list
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
	tile_button = TileButton(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 37, img_list[i], 1)
	button_list.append(tile_button)
	button_col += 1
	if button_col == 3:
		button_row += 1
		button_col = 0

run = True
while run:

	clock.tick(FPS)

	draw_bg()
	if show_grid: draw_grid()
	draw_world()

	draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 100)
	draw_text(f'Page: {page}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 70)
	draw_text('Press S to save and L to load a level. Press UP or DOWN to change it.', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 40)

	#draw tile panel and tiles
	pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

	#BUTTONS
	# Tiles
	button_count = 0
	for button_count, i in enumerate(button_list):
		if i.draw(screen):
			current_tile = button_count
	# Pages
	prev_button.draw(screen)
	next_button.draw(screen)

	#highlight the selected tile
	pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

	#scroll the map
	if scroll_left == True and scroll > 0:
		scroll -= 5 * scroll_speed
	if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
		scroll += 5 * scroll_speed

	#add new tiles to the screen
	#get mouse position
	pos = pygame.mouse.get_pos()
	x = (pos[0] + scroll) // TILE_SIZE
	y = pos[1] // TILE_SIZE

	#check that the coordinates are within the tile area
	if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
		#update tile value
		if pygame.mouse.get_pressed()[0] == 1:
			if world_data[y][x] != current_tile:
				world_data[y][x] = current_tile
		if pygame.mouse.get_pressed()[2] == 1:
			world_data[y][x] = -1

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			if event.key == pygame.K_DOWN and level > 0:
				level -= 1
			# if event.key == pygame.K_LEFT:
			# 	scroll_left = True
			# if event.key == pygame.K_RIGHT:
			# 	scroll_right = True
			# if event.key == pygame.K_RSHIFT:
			# 	scroll_speed = 5
			if event.key == pygame.K_g:
				show_grid = not show_grid
			if event.key == pygame.K_s:
				# save level data
				with open(f'level_{level}.csv', 'w', newline='') as csvfile:
					writer = csv.writer(csvfile, delimiter = ',')
					for row in world_data:
						writer.writerow(row)
				print("Level saved!")
			if event.key == pygame.K_l:
				# load in level data - reset scroll back to the start of the level
				scroll = 0
				with open(f'level_{level}.csv', newline='') as csvfile:
					reader = csv.reader(csvfile, delimiter = ',')
					for x, row in enumerate(reader):
						for y, tile in enumerate(row):
							world_data[x][y] = int(tile)
				print("Level loaded!")
				
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT:
				scroll_left = False
			if event.key == pygame.K_RIGHT:
				scroll_right = False
			if event.key == pygame.K_RSHIFT:
				scroll_speed = 1

	pygame.display.update()

pygame.quit()

