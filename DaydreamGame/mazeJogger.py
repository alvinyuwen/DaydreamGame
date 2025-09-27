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
    
    def carve (x,y):
        dirs = [(2,0),(-2,0),(0,2),(0,-2)]
        random.shuffle(dirs)
        for dx,dy in dirs:
            nx,ny = x+dx,y+dy
            if 0<nx<cols-1 and 0<ny<rows-1 and grid[ny][nx]==1:
                grid[ny][nx] = 0
                grid[y+dy//2][x+dx//2] = 0
                carve(nx,ny)

    start = (1,1)
    exit_pos = (cols-2, rows-2)
    grid[start[1]][start[0]] = 0
    grid[exit_pos[1]][exit_pos[0]] = 0
    carve(*start)

    path = find_path(grid, start, exit_pos)

    placed = 0
    while placed<trap_count:
        x = random.randint(1,cols-2)
        y = random.randint(1,rows-2)
        if grid[y][x]==0 and (x,y) not in path:
            grid[y][x] = "T"
            placed += 1

    return {"grid":grid,"start":start,"exit":exit_pos}

def find_path(grid, start, goal):
    W = len(grid[0])
    H = len(grid)
    q = deque()
    q.append(start)
    prev = {start: None}
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    while q:
        x,y = q.popleft()
        if (x,y)==goal:
            break
        for dx,dy in dirs:
            nx,ny = x+dx,y+dy
            if 0<=nx<W and 0<=ny<H and grid[ny][nx]!=1 and (nx,ny) not in prev:
                prev[(nx,ny)] = (x,y)
                q.append((nx,ny))
    if goal not in prev:
        return []
    path = []
    cur = goal
    while cur:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path
