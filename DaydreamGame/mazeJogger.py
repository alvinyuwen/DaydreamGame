import pygame
import sys
import random
from collections import deque

# -------- CONFIG ----------
TILE = 32
COLUMNS = 25
ROWS = 20
WIDTH = TILE * COLUMNS
HEIGHT = TILE * ROWS + 120
FPS = 60

STARTING_BASE_HEALTH = 6
TOTAL_LEVELS = 6

ABILITY_GAIN = "gain"
ABILITY_BREAK = "break"
ABILITY_DRAW = "draw"

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (160,160,160)
GREEN = (50,200,50)
RED = (220,50,50)
BLUE = (50,120,220)
PATH_COLOR = (180,230,250)
YELLOW = (250,230,50)

# --------MAZE GENERATOR--------

def generate_maze(cols, rows, trap_count):
    grid = [[1 for _ in range(cols)] for _ in range(rows)]
