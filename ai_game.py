import pygame
import random
import math
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT, GRID_SIZE = 800, 600, 20
SNAKE_COLOR, FOOD_COLOR, BARRIER_COLOR = (0, 255, 0), (255, 0, 0), (255, 255, 0)
FPS = 10

# Directions
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

# Load sound effects
eat_sound = pygame.mixer.Sound('audio/eat_special_sound.mp3')
collision_sound = pygame.mixer.Sound('audio/eat_sound.mp3')
game_over_sound = pygame.mixer.Sound('audio/game_over.mp3')

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
        while len(barriers) < 5:  # Limit the number of barriers
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

# Game Loop
def main():
    clock = pygame.time.Clock()
    snake = Snake()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Snake Game")

    running = True
    while running:
        screen.fill((0, 0, 0))
        
        # Draw the snake
        for segment in snake.body:
            pygame.draw.rect(screen, SNAKE_COLOR, (segment[0] * (WIDTH // GRID_SIZE), segment[1] * (HEIGHT // GRID_SIZE), WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE))
        
        # Draw food
        food_x, food_y = snake.food_pos
        pygame.draw.rect(screen, FOOD_COLOR, (food_x * (WIDTH // GRID_SIZE), food_y * (HEIGHT // GRID_SIZE), WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE))
        
        # Draw barriers
        for barrier in snake.barriers:
            pygame.draw.rect(screen, BARRIER_COLOR, (barrier[0] * (WIDTH // GRID_SIZE), barrier[1] * (HEIGHT // GRID_SIZE), WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not snake.move():
            # If the snake can't move, display Game Over message
            game_over_sound.play()  # Play game over sound
            font = pygame.font.SysFont(None, 55)
            game_over_surface = font.render('Game Over!', True, (255, 0, 0))
            screen.blit(game_over_surface, (WIDTH // 4, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.delay(2000)  # Wait for 2 seconds before quitting
            running = False
        else:
            pygame.display.flip()
            clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
