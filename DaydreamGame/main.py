import pygame
import sys
import random
import asyncio
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
    while placed < trap_count:
        x = random.randint(1,cols-2)
        y = random.randint(1,rows-2)
        if grid[y][x] == 0 and (x,y) not in path:
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
        if (x,y) == goal:
            break
        for dx,dy in dirs:
            nx,ny = x+dx,y+dy
            if 0<=nx<W and 0<=ny<H and grid[ny][nx] != 1 and (nx,ny) not in prev:
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

# ---------- Game Class ----------
class MazeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("MazeJoggers")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.bigfont = pygame.font.SysFont(None, 64)

        self.reset_game()
        self.state = "title"

    def reset_game(self):
        self.current_level_index = 0
        self.base_health = STARTING_BASE_HEALTH
        self.abilities = {ABILITY_GAIN:2, ABILITY_BREAK:2, ABILITY_DRAW:1}
        self.awaiting_break_direction = False
        self.start_level()

    def start_level(self):
        traps = 15 + self.current_level_index*5
        self.level = generate_maze(COLUMNS, ROWS, traps)
        self.grid = self.level["grid"]
        self.player_x, self.player_y = self.level["start"]
        self.exit = self.level["exit"]
        self.health = self.base_health
        self.path_hint = None
        self.revealed_path_timer = 0
        self.move_delay = 0
        self.timer_running = False
        self.time_limit = max(5, 45 - (self.current_level_index*5))  # avoid negative
        self.time_left = self.time_limit
        self.start_ticks = 0
        self.flash_red_timer = 0  # for trap hit effect

    def draw_grid(self):
        for y,row in enumerate(self.grid):
            for x,cell in enumerate(row):
                rect = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
                if cell == 1:
                    pygame.draw.rect(self.screen, GRAY, rect)
                else:
                    pygame.draw.rect(self.screen, BLACK, rect)
        ex,ey = self.exit
        pygame.draw.rect(self.screen, GREEN, (ex*TILE, ey*TILE, TILE, TILE))
        if self.path_hint:
            for (x,y) in self.path_hint:
                pygame.draw.rect(self.screen, PATH_COLOR, (x*TILE+8, y*TILE+8, TILE-16, TILE-16))
        pygame.draw.ellipse(self.screen, BLUE, (self.player_x*TILE+4,self.player_y*TILE+4,TILE-8,TILE-8))

    def draw_ui(self):
        panel_top = ROWS*TILE + 10
        self.screen.fill((20,20,20),(0,ROWS*TILE,WIDTH,HEIGHT-ROWS*TILE))
        txt = self.font.render(f"Level {self.current_level_index+1}/{TOTAL_LEVELS}", True, WHITE)
        self.screen.blit(txt,(10,panel_top))
        txt = self.font.render(f"Health: {self.health}", True, WHITE)
        self.screen.blit(txt,(160,panel_top))
        txt = self.font.render(
            f"Abilities: Gain+{self.abilities[ABILITY_GAIN]}  Break+{self.abilities[ABILITY_BREAK]}  Draw+{self.abilities[ABILITY_DRAW]}",
            True, WHITE
        )
        self.screen.blit(txt,(320,panel_top))
        txt = self.font.render(f"Time Left: {self.time_left}", True, YELLOW)
        self.screen.blit(txt,(10,panel_top+30))

    def draw_title(self):
        self.screen.fill(BLACK)
        title = self.bigfont.render("MazeJoggers", True, GREEN)
        self.screen.blit(title,(WIDTH//2-150,100))
        instructions = [
            "Navigate through 6 mazes. Each level you lose 1 base health.",
            "Invisible traps are hidden off the correct path!",
            "Abilities:",
            "1: Gain one life (temporary for current level).",
            "2: Break wall (press an arrow/WASD after to choose direction).",
            "3: Draw path (shows shortest path to exit temporarily).",
            "Controls: Arrow Keys or WASD to move (hold to move faster).",
            "Timer: 45s on L1, decreases by 5s each new level.",
            "Press SPACE to Start"
        ]
        for i,line in enumerate(instructions):
            txt = self.font.render(line, True, WHITE)
            self.screen.blit(txt,(60,200+i*30))
        pygame.display.flip()

    def draw_victory(self):
        block_size = 50
        for y in range(0,HEIGHT,block_size):
            for x in range(0,WIDTH,block_size):
                color = (random.randint(50,255),random.randint(50,255),random.randint(50,255))
                pygame.draw.rect(self.screen,color,(x,y,block_size,block_size))
        msg = self.bigfont.render("WINNER", True, BLACK)
        self.screen.blit(msg,(WIDTH//2-120,HEIGHT//2-40))
        txt = self.font.render("Press R to restart", True, BLACK)
        self.screen.blit(txt,(WIDTH//2-90,HEIGHT//2+40))
        pygame.display.flip()

    def draw_gameover(self):
        self.screen.fill(BLACK)
        text = self.bigfont.render("GAME OVER", True, RED)
        self.screen.blit(text,(WIDTH//2-140,HEIGHT//2-40))
        msg = self.font.render("Press R to restart", True, WHITE)
        self.screen.blit(msg,(WIDTH//2-90,HEIGHT//2+40))
        pygame.display.flip()

    def try_move(self,dx,dy):
        nx,ny = self.player_x+dx, self.player_y+dy
        if 0<=nx<COLUMNS and 0<=ny<ROWS and self.grid[ny][nx] != 1:
            self.player_x, self.player_y = nx, ny
            if not self.timer_running:
                self.timer_running = True
                self.start_ticks = pygame.time.get_ticks()
            if (nx,ny) == self.exit:
                self.current_level_index += 1
                if self.current_level_index >= TOTAL_LEVELS:
                    self.state = "victory"
                else:
                    self.base_health -= 1
                    self.start_level()
            if self.grid[ny][nx] == "T":
                self.lose_health(1)

    def lose_health(self,amt):
        self.health -= amt
        self.flash_red_timer = FPS // 4
        if self.health <= 0:
            self.state = "gameover"

    def use_gain(self):
        if self.abilities[ABILITY_GAIN] > 0:
            self.abilities[ABILITY_GAIN] -= 1
            self.health += 1
            return True
        return False

    def start_break(self):
        if self.abilities[ABILITY_BREAK] > 0:
            self.awaiting_break_direction = True
            return True
        return False

    def finish_break(self,dx,dy):
        if not self.awaiting_break_direction:
            return False
        nx,ny = self.player_x+dx, self.player_y+dy
        if 0<=nx<COLUMNS and 0<=ny<ROWS and self.grid[ny][nx] == 1:
            self.grid[ny][nx] = 0
            self.abilities[ABILITY_BREAK] -= 1
            self.awaiting_break_direction = False
            return True
        self.awaiting_break_direction = False
        return False

    def use_draw(self):
        if self.abilities[ABILITY_DRAW] <= 0:
            return False
        self.path_hint = find_path(self.grid, (self.player_x, self.player_y), self.exit)
        self.revealed_path_timer = FPS * 8
        self.abilities[ABILITY_DRAW] -= 1
        return True

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if self.state == "title" and ev.key == pygame.K_SPACE:
                    self.state = "playing"
                elif self.state in ("gameover","victory"):
                    if ev.key == pygame.K_r:
                        self.reset_game()
                        self.state = "title"
                elif self.state == "playing":
                    if ev.key == pygame.K_1:
                        self.use_gain()
                    elif ev.key == pygame.K_2:
                        self.start_break()
                    elif ev.key == pygame.K_3:
                        self.use_draw()
                    elif self.awaiting_break_direction:
                        if ev.key in (pygame.K_UP, pygame.K_w):
                            self.finish_break(0,-1)
                        elif ev.key in (pygame.K_DOWN, pygame.K_s):
                            self.finish_break(0,1)
                        elif ev.key in (pygame.K_LEFT, pygame.K_a):
                            self.finish_break(-1,0)
                        elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                            self.finish_break(1,0)

    def update(self):
        if self.state == "playing":
            if self.flash_red_timer > 0:
                self.flash_red_timer -= 1
                return  # pause movement/timer while flashing

            keys = pygame.key.get_pressed()
            if not self.awaiting_break_direction:
                self.move_delay -= 1
                if self.move_delay <= 0:
                    dx = dy = 0
                    if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
                    if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
                    if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
                    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
                    if dx != 0 or dy != 0:
                        self.try_move(dx,dy)
                        self.move_delay = 6

            if self.revealed_path_timer > 0:
                self.revealed_path_timer -= 1
                if self.revealed_path_timer <= 0:
                    self.path_hint = None

            if self.timer_running:
                seconds_passed = (pygame.time.get_ticks() - self.start_ticks) // 1000
                remaining = self.time_limit - seconds_passed
                if remaining <= 0:
                    self.state = "gameover"
                else:
                    self.time_left = remaining

    def draw(self):
        if self.state == "title":
            self.draw_title()
        elif self.state == "victory":
            self.draw_victory()
        elif self.state == "gameover":
            self.draw_gameover()
        elif self.state == "playing":
            if self.flash_red_timer > 0:
                self.screen.fill(RED)
            else:
                self.screen.fill(BLACK)
                self.draw_grid()
                self.draw_ui()
            pygame.display.flip()

    # async run for pygbag/browser
    async def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            await asyncio.sleep(0)  # yield to event loop

# ------------ Entry Point ------------
async def main():
    game = MazeGame()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())






























































































































































































































































































