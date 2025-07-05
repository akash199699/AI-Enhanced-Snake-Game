import pygame
import random
import os

# Initialize Pygame
pygame.init()
# Load sounds
pygame.mixer.init()
eat_sound = pygame.mixer.Sound('audio/eat_sound.mp3')  # Sound for eating food
eat_special_sound = pygame.mixer.Sound(r'audio/eat_special_sound.mp3')  # Sound for eating special food
game_over_sound = pygame.mixer.Sound(r'audio/game_over.mp3')  # Sound for game over

# pygame.mixer.music.load(r'audio/background_music.mp3')  # Background music
# pygame.mixer.music.play(-1)  # Play music indefinitely

# High score file
HIGH_SCORE_FILE = "stats/high_score.txt"

# Screen dimensions and grid size
GRID_SIZE = 20
CELL_SIZE = 30
SCREEN_SIZE = GRID_SIZE * CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Directions for snake movement
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Game modes
FREE_PLAY = 0
TIMED_MODE = 1

# Constants for grid values
EMPTY = 0        # Represents an empty cell in the grid
OBSTACLE = 1     # Represents a snake segment or other obstacles
FOOD = 2         # Represents food on the grid
SPECIAL_FOOD = 3 # Represents special food on the grid


# Initialize screen
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("AI Snake Game")

# Clock for controlling the game's frame rate
clock = pygame.time.Clock()

def load_high_score():
    """Load high score from a file."""
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as file:
            return int(file.read().strip())
    return 0

def save_high_score(score):
    """Save high score to a file."""
    with open(HIGH_SCORE_FILE, 'w') as file:
        file.write(str(score))

# Snake class to manage the snake's properties and movement
class Snake:
    def __init__(self):
        self.body = [(10, 10)]  # Starting position in the middle
        self.direction = RIGHT
        self.growing = False

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        
        # Grow the snake if it just ate food
        if self.growing:
            self.body = [new_head] + self.body
            self.growing = False
        else:
            self.body = [new_head] + self.body[:-1]

    def grow(self):
        self.growing = True

    def change_direction(self, direction):
        if (direction[0], direction[1]) != (-self.direction[0], -self.direction[1]):
            self.direction = direction

    def check_collision(self):
        head = self.body[0]
        # Check if the snake hits itself or the walls
        if head in self.body[1:] or not (0 <= head[0] < GRID_SIZE and 0 <= head[1] < GRID_SIZE):
            return True
        return False

# Food class to manage food spawning and consumption
class Food:
    def __init__(self):
        self.position = self.random_position()

    def random_position(self):
        return (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

    def draw(self):
        x, y = self.position
        pygame.draw.rect(screen, RED, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

class SpecialFood:
    def __init__(self):
        self.position = None
        self.active = False
        self.spawn_time = 0
        self.lifetime = 100  # Special food appears for a limited time (e.g., 100 frames)

    def spawn(self):
        self.position = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        self.active = True
        self.spawn_time = pygame.time.get_ticks()  # Record when the special food spawns

    def update(self):
        if self.active:
            # Remove the special food if its lifetime has passed
            if pygame.time.get_ticks() - self.spawn_time > self.lifetime * 100:
                self.active = False

    def draw(self):
        if self.active:
            x, y = self.position
            pygame.draw.rect(screen, YELLOW, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

class Barrier:
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = start_pos
        self.direction = 1  # 1 for moving right/down, -1 for left/up

    def move(self):
        # Move the barrier back and forth
        if self.current_pos[0] < self.end_pos[0] and self.direction == 1:
            self.current_pos = (self.current_pos[0] + 1, self.current_pos[1])
            if self.current_pos[0] == self.end_pos[0]:
                self.direction = -1
        elif self.current_pos[0] > self.start_pos[0] and self.direction == -1:
            self.current_pos = (self.current_pos[0] - 1, self.current_pos[1])
            if self.current_pos[0] == self.start_pos[0]:
                self.direction = 1

    def draw(self):
        x, y = self.current_pos
        pygame.draw.rect(screen, WHITE, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def show_menu():
    menu_running = True
    while menu_running:
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 55)

        # Define menu options
        options = [
            ("Select Game Mode", (GRID_SIZE * CELL_SIZE // 2, GRID_SIZE * CELL_SIZE // 4)),
            ("Press 1 for Free-Play", (GRID_SIZE * CELL_SIZE // 2, GRID_SIZE * CELL_SIZE // 2)),
            ("Press 2 for Timed Mode", (GRID_SIZE * CELL_SIZE // 2, GRID_SIZE * CELL_SIZE * 3 // 4)),
        ]

        # Render options
        for text, position in options:
            rendered_text = font.render(text, True, WHITE)
            screen.blit(rendered_text, (position[0] - rendered_text.get_width() // 2, position[1]))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_loop(FREE_PLAY)  # Start game in Free-Play mode
                    menu_running = False
                elif event.key == pygame.K_2:
                    game_loop(TIMED_MODE)  # Start game in Timed mode
                    menu_running = False


# Function to show game over screen
def game_over(score, high_score):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 55)
    game_over_text = font.render("Game Over!", True, WHITE)
    score_text = font.render(f"Your Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    quit_text = font.render("Press Q to Quit", True, WHITE)

    screen.blit(game_over_text, (GRID_SIZE * CELL_SIZE // 2 - game_over_text.get_width() // 2, GRID_SIZE * CELL_SIZE // 3))
    screen.blit(score_text, (GRID_SIZE * CELL_SIZE // 2 - score_text.get_width() // 2, GRID_SIZE * CELL_SIZE // 2))
    screen.blit(high_score_text, (GRID_SIZE * CELL_SIZE // 2 - high_score_text.get_width() // 2, GRID_SIZE * CELL_SIZE * 2 // 3))
    screen.blit(restart_text, (GRID_SIZE * CELL_SIZE // 2 - restart_text.get_width() // 2, GRID_SIZE * CELL_SIZE * 5 // 6))
    screen.blit(quit_text, (GRID_SIZE * CELL_SIZE // 2 - quit_text.get_width() // 2, GRID_SIZE * CELL_SIZE * 5 // 6+40))
    
    pygame.display.flip()
    pygame.mixer.music.stop()  # Stop background music
    game_over_sound.play()  # Play game over sound

    # # Wait for a few seconds before quitting
    # pygame.time.delay(2000)  # Delay for 2 seconds
    # pygame.quit()

    waiting_for_restart = True
    while waiting_for_restart:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Press R to restart
                    waiting_for_restart = False
                    show_menu()  # Restart the game
                elif event.key == pygame.K_q:  # Press Q to quit
                    pygame.quit()
                    exit()

# Main game loop 
def game_loop(mode=FREE_PLAY):
    snake = Snake()
    food = Food()
    special_food = SpecialFood()
    barriers = []  # No barriers in free-play mode, add them in timed or AI mode
    running = True
    score = 0
    high_score = load_high_score()  # Load high score from file
    special_food_spawn_interval = 5000  # Spawn special food every 5 seconds
    level = 1
    speed = 10  # Initial speed
    start_time = pygame.time.get_ticks()  # Record the start time for timed mode
    game_duration = 60000  # 60 seconds for timed mode

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over_sound.play()  # Play game over sound
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction(UP)
                elif event.key == pygame.K_DOWN:
                    snake.change_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.change_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction(RIGHT)
                elif event.key == pygame.K_p:  # Pause
                    paused = True
                    while paused:
                        for pause_event in pygame.event.get():
                            if pause_event.type == pygame.KEYDOWN and pause_event.key == pygame.K_p:
                                paused = False
                            elif pause_event.type == pygame.QUIT:
                                paused = False
                        screen.fill(BLACK)
                        pause_text = font.render("Game Paused", True, WHITE)
                        screen.blit(pause_text, (GRID_SIZE * CELL_SIZE // 2 - pause_text.get_width() // 2, GRID_SIZE * CELL_SIZE // 2))
                        pygame.display.flip()

        snake.move()

        # Spawn special food at intervals
        if pygame.time.get_ticks() % special_food_spawn_interval < 50 and not special_food.active:
            special_food.spawn()

        # Update special food lifetime
        special_food.update()

        # Move barriers in timed mode
        if mode == TIMED_MODE:
            for barrier in barriers:
                barrier.move()

        # Check if snake eats the food
        if snake.body[0] == food.position:
            snake.grow()
            score += 1
            eat_sound.play()  # Play eat sound
            food = Food()  # Spawn new food

        # Check if snake eats the special food
        if special_food.active and snake.body[0] == special_food.position:
            snake.grow()
            snake.grow()  # Snake grows by 2 units
            score += 5  # Higher score for special food
            eat_special_sound.play()  # Play eat sound
            special_food.active = False  # Remove special food after eating

        # Check for collisions with barriers in timed mode
        if mode == TIMED_MODE:
            for barrier in barriers:
                if snake.body[0] == barrier.current_pos:
                    game_over_sound.play()  # Play game over sound
                    running = False

        # Check for collisions
        if snake.check_collision():
            game_over_sound.play()  # Play game over sound
            running = False

        # Draw everything
        screen.fill(BLACK)
        for segment in snake.body:
            pygame.draw.rect(screen, GREEN, pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        food.draw()
        special_food.draw()  # Draw special food if it's active

        # Draw barriers in timed mode
        if mode == TIMED_MODE:
            for barrier in barriers:
                barrier.draw()

        # Display the score
        font = pygame.font.SysFont(None, 35)
        score_text = font.render(f"Score: {score}", True, WHITE)
        high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(score_text, (5, 5))
        screen.blit(high_score_text, (5, 40))

        # Display the timer in timed mode
        if mode == TIMED_MODE:
            elapsed_time = pygame.time.get_ticks() - start_time
            remaining_time = max(0, game_duration - elapsed_time) / 1000  # Convert to seconds
            timer_text = font.render(f"Time Left: {remaining_time:.1f}s", True, WHITE)
            screen.blit(timer_text, (SCREEN_SIZE - 150, 10))  # Positioning at the top right

        # Increase difficulty
        if mode == TIMED_MODE and score > level * 5:  # Increase difficulty every 5 points
            level += 1
            speed += 2  # Increase snake speed
            barriers.append(Barrier((random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)),
                                    (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))))  # Add a new barrier

        # End timed mode after duration
        if mode == TIMED_MODE and pygame.time.get_ticks() - start_time > game_duration:
            running = False

        pygame.display.flip()
        clock.tick(speed)  # Control the speed of the snake
    
    # Check if current score is higher than the high score
    if score > high_score:
        high_score = score
        save_high_score(high_score)  # Save the new high score
    
    game_over(score, high_score)  # Show the game over screen with the score

    pygame.quit()

# Call the menu function before starting the game loop
show_menu()

# Start the game loop
game_loop()

