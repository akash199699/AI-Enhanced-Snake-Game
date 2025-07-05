import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT, GRID_SIZE = 800, 600, 20
SNAKE_COLOR, FOOD_COLOR, BARRIER_COLOR = (0, 255, 0), (255, 0, 0), (255, 255, 0)
FPS = 10
BUTTON_COLOR = (0, 128, 255)
BUTTON_HOVER_COLOR = (0, 102, 204)
TEXT_COLOR = (255, 255, 255)

# Directions
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

# Initialize Pygame screen and set title
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Snake Navigator")

# Load sound effects
eat_sound = pygame.mixer.Sound('audio/eat_special_sound.mp3')
collision_sound = pygame.mixer.Sound('audio/eat_sound.mp3')
game_over_sound = pygame.mixer.Sound('audio/game_over.mp3')

# Load images for snake head and body
logo_img = pygame.image.load('img/head.png')
head_img = pygame.image.load('img/head.png').convert_alpha()
body_img = pygame.image.load('img/bodyf.png').convert_alpha()
food_image = pygame.image.load('img/food.png')
barrier_image = pygame.image.load('img/mine.png')

# Resize images to fit the grid size
logo_img = pygame.transform.scale(head_img, (400, 400))
head_img = pygame.transform.scale(head_img, (GRID_SIZE, GRID_SIZE))
body_img = pygame.transform.scale(body_img, (GRID_SIZE, GRID_SIZE))
food_image = pygame.transform.scale(food_image, (GRID_SIZE, GRID_SIZE))
barrier_image = pygame.transform.scale(barrier_image, (GRID_SIZE, GRID_SIZE))

# A* Algorithm Implementation
class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start node
        self.h = 0  # Heuristic cost to goal node
        self.f = 0  # Total cost

def astar(start, goal, grid):
    open_list = []
    closed_list = []

    start_node = Node(start)
    goal_node = Node(goal)
    open_list.append(start_node)

    iteration_limit = 1000  # Limit iterations to prevent infinite loops
    iterations = 0

    while open_list:
        iterations += 1
        if iterations > iteration_limit:
            print("Iteration limit reached. No path found.")
            return []  # Exit if iteration limit reached

        # Get the node with the lowest f cost
        current_node = min(open_list, key=lambda o: o.f)
        open_list.remove(current_node)
        closed_list.append(current_node)

        # If we reached the goal, reconstruct the path
        if current_node.position == goal_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]  # Return reversed path

        # Generate children nodes
        for direction in [UP, DOWN, LEFT, RIGHT]:
            neighbor_pos = (current_node.position[0] + direction[0], current_node.position[1] + direction[1])

            # Check for obstacles (borders, snake body, barriers)
            if (0 <= neighbor_pos[0] < GRID_SIZE and
                0 <= neighbor_pos[1] < GRID_SIZE and
                grid[neighbor_pos[0]][neighbor_pos[1]] == 0):  # Check for obstacles
                
                neighbor_node = Node(neighbor_pos, current_node)

                if neighbor_node in closed_list:
                    continue

                neighbor_node.g = current_node.g + 1
                neighbor_node.h = (goal_node.position[0] - neighbor_node.position[0]) ** 2 + (goal_node.position[1] - neighbor_node.position[1]) ** 2
                neighbor_node.f = neighbor_node.g + neighbor_node.h

                if neighbor_node not in open_list:
                    open_list.append(neighbor_node)

    print("No valid path found.")
    return []  # No path found

class Snake:
    def __init__(self):
        self.body = [(5, 5)]
        self.direction = (0, 1)  # Moving right
        self.barriers = self.create_barriers()  # Create barriers first
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.food_pos = self.spawn_food()  # Now spawn food after barriers are created
        self.update_grid()

    def spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            # Check if the position is not occupied by the snake's body or barriers
            if pos not in self.body and pos not in self.barriers:
                return pos

    def create_barriers(self):
        barriers = []
        while len(barriers) < 10:  # Limit the number of barriers
            pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if pos not in self.body and pos not in barriers:
                barriers.append(pos)
        return barriers

    def update_grid(self):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if (x, y) in self.body or (x, y) in self.barriers:
                    self.grid[x][y] = 1  # Marking body and barriers as obstacles
                else:
                    self.grid[x][y] = 0  # Free space

    def move(self):
        if self.food_pos:
            path = astar(self.body[0], self.food_pos, self.grid)
            if path:
                next_pos = path[1]  # Get the next position to move towards
                self.body.insert(0, next_pos)
                if next_pos == self.food_pos:
                    eat_sound.play()  # Play eat sound
                    self.food_pos = self.spawn_food()  # Respawn food
                else:
                    self.body.pop()  # Remove tail if not eating
                self.update_grid()  # Update grid after moving
                return True  # Movement successful
            else:
                # No path found, move randomly
                return self.move_randomly()
        return False  # Food position is None, should not happen in the game

    def move_randomly(self):
        possible_directions = [UP, DOWN, LEFT, RIGHT]
        random.shuffle(possible_directions)  # Shuffle directions for random movement
        for direction in possible_directions:
            new_pos = (self.body[0][0] + direction[0], self.body[0][1] + direction[1])
            # Check for valid movement (not colliding with itself or barriers)
            if (0 <= new_pos[0] < GRID_SIZE and
                0 <= new_pos[1] < GRID_SIZE and
                new_pos not in self.body and
                new_pos not in self.barriers):
                self.body.insert(0, new_pos)
                self.body.pop()  # Remove the tail
                self.update_grid()  # Update the grid after moving
                return True  # Successfully moved
        collision_sound.play()  # Play collision sound if no valid move
        return False  # No valid moves available

    def check_collisions(self):
        # Check for collision with self
        if self.body[0] in self.body[1:]:
            return True
        # Check for collision with barriers
        if self.body[0] in self.barriers:
            return True
        return False

def draw_snake(screen, snake):
    """Draw the snake using head and body images."""
    for i, segment in enumerate(snake.body):
        x = segment[0] * GRID_SIZE
        y = segment[1] * GRID_SIZE
        if i == 0:
            # Draw head
            screen.blit(head_img, (x, y))
        else:
            # Draw body segment
            screen.blit(body_img, (x, y))

def draw_button(screen, text, x, y, w, h, hover=False):
    color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, (x, y, w, h))
    font = pygame.font.SysFont(None, 40)
    text_surface = font.render(text, True, TEXT_COLOR)
    screen.blit(text_surface, (x + (w - text_surface.get_width()) // 2, y + (h - text_surface.get_height()) // 2))

def main_menu(screen):
    while True:
        screen.fill((0, 0, 0))
        mouse_pos = pygame.mouse.get_pos()
        play_button_hover = 200 <= mouse_pos[0] <= 600 and 100 <= mouse_pos[1] <= 500
        
        # Draw Logo
        screen.blit(logo_img, (WIDTH // 2 - logo_img.get_width() // 2, 150))  # Center the logo

        # Draw Title
        title_font = pygame.font.SysFont(None, 60)
        title_surface = title_font.render("AI Snake Game", True, TEXT_COLOR)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 100))

        # Draw Play Button
        draw_button(screen, "Play", 300, 450, 200, 50, hover=play_button_hover)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and play_button_hover:
                return True  # Start the game

        pygame.display.flip()

def game_over_screen(screen):
    # Fill the screen with black color
    screen.fill((0, 0, 0))
    
    # Render the "Game Over" text
    font = pygame.font.SysFont(None, 55)
    text = font.render("Game Over", True, (255, 255, 255))  # White color
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    # Draw restart and quit buttons
    draw_button(screen, "Restart", WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    draw_button(screen, "Quit", WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)

    pygame.display.flip()  # Update the display

    while True:  # Keep the game over screen open
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False  # Exit the game
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Check for button clicks
                if (WIDTH // 2 - 100 <= mouse_pos[0] <= WIDTH // 2 + 100 and 
                    HEIGHT // 2 + 50 <= mouse_pos[1] <= HEIGHT // 2 + 100):
                    return True  # Restart the game
                if (WIDTH // 2 - 100 <= mouse_pos[0] <= WIDTH // 2 + 100 and 
                    HEIGHT // 2 + 120 <= mouse_pos[1] <= HEIGHT // 2 + 170):
                    pygame.quit()
                    return False  # Quit the game


def main_game():
    snake = Snake()
    score = 0
    clock = pygame.time.Clock()
    game_started = True

    while game_started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == pygame.K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT
                elif event.key == pygame.K_p:  # Pause the game
                    pause_game(snake)

        # Move the snake
        if snake.move():
            if snake.check_collisions():
                game_over_screen(screen)  # Display game over screen
                game_over_sound.play()
                snake = Snake()  # Restart the game
            score += 1  # Increment score for each food eaten

        # Drawing
        screen.fill((0, 0, 0))
        draw_snake(screen, snake)

        # Draw food
        food_x = snake.food_pos[0] * GRID_SIZE
        food_y = snake.food_pos[1] * GRID_SIZE
        # pygame.draw.rect(screen, FOOD_COLOR, (food_x, food_y, GRID_SIZE, GRID_SIZE))
        screen.blit(food_image, (food_x, food_y))  # Draw the food image

        # Draw barriers
        for barrier in snake.barriers:
            barrier_x = barrier[0] * GRID_SIZE
            barrier_y = barrier[1] * GRID_SIZE
            # pygame.draw.rect(screen, BARRIER_COLOR, (barrier_x, barrier_y, GRID_SIZE, GRID_SIZE))
            screen.blit(barrier_image, (barrier_x, barrier_y))

        pygame.display.flip()
        clock.tick(FPS)

def pause_game(snake):
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:  # Press P to unpause
                paused = False
        # You can display a pause message or any other UI elements here
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 55)
        text = font.render("Paused. Press P to continue.", True, TEXT_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.delay(100)

def main():
    while True:
        if main_menu(screen):
            main_game()  # Start the main game

if __name__ == "__main__":
    main()
