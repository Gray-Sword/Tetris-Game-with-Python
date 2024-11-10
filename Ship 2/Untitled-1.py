import pygame
import random
import sys

# Game constants
WIDTH, HEIGHT = 400, 600
BLOCK_SIZE = 30
ROWS, COLS = HEIGHT // BLOCK_SIZE, 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRID_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)

# Tetris shapes and colors
SHAPES = [
    [[1, 1, 1, 1]],  # I shape
    [[1, 1, 0], [0, 1, 1]],  # Z shape
    [[0, 1, 1], [1, 1, 0]],  # S shape
    [[1, 1, 1], [0, 1, 0]],  # T shape
    [[1, 1, 1], [1, 0, 0]],  # L shape
    [[1, 1, 1], [0, 0, 1]],  # J shape
    [[1, 1], [1, 1]]  # O shape
]

COLORS = [
    (0, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (255, 165, 0),
    (0, 0, 255),
    (128, 0, 128),
    (255, 255, 0)
]

class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0
    
    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Enhanced Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.hold_piece = None
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.drop_speed = 500
        self.last_drop_time = pygame.time.get_ticks()

    def reset_game(self):
        self.grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.hold_piece = None
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.drop_speed = 500

    def check_collision(self, piece, dx=0, dy=0):
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = piece.x + j + dx
                    new_y = piece.y + i + dy
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x] != BLACK:
                        return True
        return False

    def freeze_piece(self):
        for i, row in enumerate(self.current_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.color
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()
        if self.check_collision(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        full_rows = [i for i, row in enumerate(self.grid) if all(cell != BLACK for cell in row)]
        for row in full_rows:
            del self.grid[row]
            self.grid.insert(0, [BLACK for _ in range(COLS)])
        self.lines_cleared += len(full_rows)
        self.update_score(len(full_rows))
        if self.lines_cleared >= self.level * 10:
            self.level += 1
            self.drop_speed = max(100, self.drop_speed - 50)

    def update_score(self, lines):
        self.score += (100 * lines) * self.level

    def draw_grid(self):
        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(self.screen, self.grid[y][x], rect)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

    def draw_piece(self, piece, x_offset=0, y_offset=0):
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect((piece.x + j + x_offset) * BLOCK_SIZE, 
                                       (piece.y + i + y_offset) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.screen, piece.color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)

    def draw_next_piece(self):
        self.draw_piece(self.next_piece, x_offset=COLS + 1)

    def move_piece(self, dx, dy):
        if not self.check_collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
        elif dy > 0:
            self.freeze_piece()

    def rotate_piece(self):
        original_shape = self.current_piece.shape
        self.current_piece.rotate()
        if self.check_collision(self.current_piece):
            self.current_piece.shape = original_shape

    def run(self):
        while True:
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_next_piece()
            self.draw_score()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move_piece(0, 1)
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        while not self.check_collision(self.current_piece, 0, 1):
                            self.move_piece(0, 1)
                        self.freeze_piece()
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()

            if not self.game_over and pygame.time.get_ticks() - self.last_drop_time > self.drop_speed:
                self.move_piece(0, 1)
                self.last_drop_time = pygame.time.get_ticks()

            pygame.display.update()
            self.clock.tick(30)

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        level_text = self.font.render(f"Level: {self.level}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
