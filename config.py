
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
COLOR_BG = (36,55,117)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRAVITY = 10
TILE_SIZE = 32
SOLID_TILES = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]

CONTROL_KEYS = {
    'P1' : {
        'JUMP'          : 'K_w',
        'WALK_LEFT'     : 'K_a',
        'WALK_RIGHT'    : 'K_d',
        'CROUCH'        : 'K_s',
        'BLOCK'         : 'K_z',
        'PUNCH'         : 'K_x',
        'KICK'          : 'K_c' 
    },
    'P2' : {
        'JUMP'          : 'K_o',
        'WALK_LEFT'     : 'K_k',
        'WALK_RIGHT'    : 'K_l',
        'CROUCH'        : 'K_SEMICOLON',
        'BLOCK'         : 'K_m',
        'PUNCH'         : 'K_COMMA',
        'KICK'          : 'K_PERIOD' 
    },
}