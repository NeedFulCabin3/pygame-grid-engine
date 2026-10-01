import json
import os
import random
import sys
import pygame

# Configuration Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 12

# Color Palette (RGB)
COLOR_BG = (18, 18, 24)
COLOR_GRID = (28, 28, 38)
COLOR_SNAKE_HEAD = (46, 204, 113)
COLOR_SNAKE_BODY = (39, 174, 96)
COLOR_FOOD = (231, 76, 60)
COLOR_TEXT = (236, 240, 241)
COLOR_ACCENT = (241, 196, 15)

HIGH_SCORE_FILE = "highscore.json"


def generate_synth_sound(frequency: float, duration: float, volume: float = 0.3) -> pygame.mixer.Sound:
    """Generates a simple audio tone synthetically so no external .wav files are required."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buffer = bytearray()
    
    for i in range(n_samples):
        # Generate square wave sample
        t = float(i) / sample_rate
        value = 127 if (int(t * frequency * 2) % 2) == 0 else -128
        scaled = int(value * volume)
        buffer.append(scaled & 0xFF)

    return pygame.mixer.Sound(buffer=bytes(buffer))


class HighScoreManager:
    """Handles persistent high score I/O with JSON formatting."""
    
    @staticmethod
    def load_high_score() -> int:
        if not os.path.exists(HIGH_SCORE_FILE):
            return 0
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except (json.JSONDecodeError, OSError):
            return 0

    @staticmethod
    def save_high_score(score: int) -> None:
        try:
            with open(HIGH_SCORE_FILE, "w") as f:
                json.dump({"high_score": score}, f, indent=4)
        except OSError as e:
            print(f"Warning: Could not save high score to disk: {e}")


class Snake:
    """Manages snake positions, direction state, growth, and rendering."""
    
    def __init__(self):
        self.reset()

    def reset(self):
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.body = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.grow_pending = False

    def change_direction(self, new_dir: tuple[int, int]):
        # Prevent 180-degree immediate turns into self
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.next_direction = new_dir

    def update(self) -> bool:
        """Updates position. Returns False if a collision occurs."""
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Wall Collision Check
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            return False

        # Self Collision Check
        if new_head in self.body:
            return False

        self.body.insert(0, new_head)
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

        return True

    def draw(self, surface: pygame.Surface):
        for index, (x, y) in enumerate(self.body):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1)
            color = COLOR_SNAKE_HEAD if index == 0 else COLOR_SNAKE_BODY
            pygame.draw.rect(surface, color, rect, border_radius=4)


class Food:
    """Manages food placement avoiding collision with snake body."""
    
    def __init__(self):
        self.position = (0, 0)

    def respawn(self, snake_body: list[tuple[int, int]]):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_body:
                self.position = pos
                break

    def draw(self, surface: pygame.Surface):
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE + 1,
            self.position[1] * GRID_SIZE + 1,
            GRID_SIZE - 2,
            GRID_SIZE - 2
        )
        pygame.draw.ellipse(surface, COLOR_FOOD, rect)


class SnakeGame:
    """Core Game Loop & Controller Class."""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-8, channels=1, buffer=512)
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Python Snake Arcade")
        self.clock = pygame.time.Clock()
        
        self.font_main = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 24)
        self.font_large = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 48, bold=True)
        
        # Audio Initialization
        try:
            self.snd_eat = generate_synth_sound(523.25, 0.08, 0.2)  # C5 tone
            self.snd_over = generate_synth_sound(146.83, 0.35, 0.4)  # D3 tone
        except Exception:
            self.snd_eat = None
            self.snd_over = None

        self.snake = Snake()
        self.food = Food()
        self.food.respawn(self.snake.body)
        
        self.score = 0
        self.high_score = HighScoreManager.load_high_score()
        self.game_over = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                else:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.snake.change_direction((0, -1))
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.change_direction((0, 1))
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.change_direction((-1, 0))
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.change_direction((1, 0))

        return True

    def reset_game(self):
        self.snake.reset()
        self.food.respawn(self.snake.body)
        self.score = 0
        self.game_over = False

    def update(self):
        if self.game_over:
            return

        alive = self.snake.update()
        if not alive:
            self.game_over = True
            if self.snd_over:
                self.snd_over.play()
            if self.score > self.high_score:
                self.high_score = self.score
                HighScoreManager.save_high_score(self.high_score)
            return

        # Food Collision Detection
        if self.snake.body[0] == self.food.position:
            self.snake.grow_pending = True
            self.score += 10
            if self.snd_eat:
                self.snd_eat.play()
            self.food.respawn(self.snake.body)

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw Grid Overlay
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))

        self.food.draw(self.screen)
        self.snake.draw(self.screen)

        # HUD (Heads-Up Display)
        score_surf = self.font_main.render(f"Score: {self.score}", True, COLOR_TEXT)
        high_surf = self.font_main.render(f"High Score: {self.high_score}", True, COLOR_ACCENT)
        self.screen.blit(score_surf, (15, 10))
        self.screen.blit(high_surf, (WINDOW_WIDTH - high_surf.get_width() - 15, 10))

        # Game Over Overlay
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            txt_title = self.font_large.render("GAME OVER", True, COLOR_FOOD)
            txt_restart = self.font_main.render("Press SPACE to Play Again or ESC to Quit", True, COLOR_TEXT)
            
            self.screen.blit(txt_title, (WINDOW_WIDTH // 2 - txt_title.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(txt_restart, (WINDOW_WIDTH // 2 - txt_restart.get_width() // 2, WINDOW_HEIGHT // 2 + 20))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SnakeGame()
    game.run()