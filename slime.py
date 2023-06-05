import sys
from queue import PriorityQueue
import numpy as np
import pygame

GRID_WIDTH = 720
GRID_HEIGHT = 720
BARRIER_PROB = 0.33 # Barrier "density". Choose from 0 to 0.367713 (percolation threshold)

UPDATE_FREQUENCY = 100  # Frequency at which the algorithm steps are updated/rendered

BACKGROUND_COLOR = (0, 0, 0)
BARRIER_COLOR = (25, 25, 25)
USER_BARRIER_COLOR = (255,255,255)
SLIME_COLOR = (194, 178, 39)
VEIN_COLOR = (161, 150, 66)
SLIME_TRAIL_COLOR = (97, 92, 46)
DARK_SLIME_COLOR = (22, 26, 10)
BUTTONS_COLOR = (110, 24, 24)
BUTTONS_HOVER_COLOR = (60, 0, 15)
FONT = "arial"

DRAWN_BARRIER_SIZE = 5

NEIGHBOR_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Map generation
def generate_barrier_map():
    barrier_array = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[1 - BARRIER_PROB, BARRIER_PROB])
    return barrier_array

# UI rendering
def clear_screen(screen, barrier_map):
    screen.fill((BACKGROUND_COLOR))
    draw_map(screen, barrier_map)
    pygame.display.update()

def draw_map(screen, barrier_map):
    barriers = np.argwhere(barrier_map == 1)
    for x, y in barriers:
        pygame.draw.rect(screen, BARRIER_COLOR, (y, x, 1, 1))

def draw_button(x, y, w, h, text, inactive_color, active_color, screen, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h))

    button_text = pygame.font.SysFont(FONT, 24, bold=True).render(text, True, (255, 248, 219))
    text_rect = button_text.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(button_text, text_rect)

# Algorithm
def dijkstra(screen, barrier_map, start, end):
    """Run Dijkstra's algorithm to find the shortest path."""
    queue = PriorityQueue()
    queue.put((0, start))
    visited = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=bool)
    previous = np.full((GRID_HEIGHT, GRID_WIDTH), fill_value=None, dtype=object)
    costs = np.full((GRID_HEIGHT, GRID_WIDTH), fill_value=float('inf'), dtype=float)
    costs[start[1], start[0]] = 0
    visited_cells = []

    iteration = 0
    update_counter = 0

    while not queue.empty():
        current_cost, current_cell = queue.get()
        visited[current_cell[1], current_cell[0]] = True
        visited_cells.append(current_cell)
        if current_cell == end:
            break

        neighbors = get_neighbors(current_cell, barrier_map)
        for neighbor in neighbors:
            distance = costs[current_cell[1], current_cell[0]] + 1
            if distance < costs[neighbor[1], neighbor[0]]:
                costs[neighbor[1], neighbor[0]] = distance
                previous[neighbor[1], neighbor[0]] = current_cell
                queue.put((distance, neighbor))

    if end not in visited_cells:
        # No path found
        return [], previous

    return visited_cells, previous

def get_neighbors(cell, barrier_map):
    """Get valid neighboring cells for a given cell."""
    x, y = cell
    valid_neighbors = []
    for dx, dy in NEIGHBOR_OFFSETS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and barrier_map[ny, nx] != 1:
            valid_neighbors.append((nx, ny))
    return valid_neighbors

# User input for barrier drawing
def get_user_barrier_input(screen, barrier_map):
    drawn_points = []
    continue_button = pygame.Rect(GRID_WIDTH - 120, GRID_HEIGHT - 70, 120, 50)
    draw_button(continue_button.x, continue_button.y, continue_button.width, continue_button.height, "Continue",
                BUTTONS_COLOR, BUTTONS_HOVER_COLOR, screen)
    running = True  # flag
    prev_point = None  # Variable to store the previous point
    drawing = True  # Flag to indicate if drawing is enabled
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if continue_button.collidepoint(mouse_pos):
                    running = False
                elif drawing:  # Only add points and lines when drawing is enabled
                    pygame.draw.circle(screen, BARRIER_COLOR, event.pos, DRAWN_BARRIER_SIZE)
                    drawn_points.append(event.pos)
                    if prev_point is not None:
                        pygame.draw.line(screen, BARRIER_COLOR, prev_point, event.pos, DRAWN_BARRIER_SIZE)
                        add_barrier_to_map(prev_point, event.pos, barrier_map)
                    prev_point = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right-click
                drawing = not drawing  # Toggle drawing state
                if drawing:
                    prev_point = None  # Reset prev_point when drawing is re-enabled
        pygame.display.update()

def add_barrier_to_map(start_point, end_point, barrier_map):
    x1, y1 = start_point
    x2, y2 = end_point
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = -1 if x1 > x2 else 1
    sy = -1 if y1 > y2 else 1
    err = dx - dy

    while x1 != x2 or y1 != y2:
        barrier_map[max(0, y1 - DRAWN_BARRIER_SIZE):y1 + DRAWN_BARRIER_SIZE + 1,
                    max(0, x1 - DRAWN_BARRIER_SIZE):x1 + DRAWN_BARRIER_SIZE + 1] = 1

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    barrier_map[max(0, y2 - DRAWN_BARRIER_SIZE):y2 + DRAWN_BARRIER_SIZE + 1,
                max(0, x2 - DRAWN_BARRIER_SIZE):x2 + DRAWN_BARRIER_SIZE + 1] = 1

# User input for start and end points
def get_user_input(screen, barrier_map):
    start = None
    end = None
    selecting_start = True
    selecting_end = False

    while selecting_start or selecting_end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if selecting_start:
                    start = mouse_pos
                    selecting_start = False
                    selecting_end = True
                elif selecting_end:
                    end = mouse_pos
                    selecting_end = False

        if start is not None:
            pygame.draw.circle(screen, (0, 255, 0), start, 5)
        if end is not None:
            pygame.draw.circle(screen, (255, 255, 255), end, 7)
        pygame.display.update()

    # Remove barriers where the points are at
    radius = 7
    if start is not None and end is not None:
        start_x, start_y = start
        barrier_map[max(0, start_y - radius):start_y + radius, max(0, start_x - radius):start_x + radius] = 0
        end_x, end_y = end
        barrier_map[max(0, end_y - radius):end_y + radius, max(0, end_x - radius):end_x + radius] = 0

    return start, end

# Draw slime
def draw_algorithm_steps(screen, barrier_map, start, end):
    visited_cells, previous = dijkstra(screen, barrier_map, start, end)
    trail_cells = []
    iteration = 0

    for cell in visited_cells:
        iteration += 1
        current_cell = cell
        while current_cell != start:
            prev_cell = previous[current_cell[1], current_cell[0]]
            if iteration % UPDATE_FREQUENCY == 0:
                pygame.draw.line(screen, VEIN_COLOR, tuple(prev_cell), tuple(current_cell), 1) # Veins
            current_cell = prev_cell
        if len(trail_cells) > iteration // 15:
            decay_cell = trail_cells.pop(0)
            pygame.draw.rect(screen, SLIME_COLOR, (cell[0], cell[1], 2, 2))  # Exploring slime
            pygame.draw.rect(screen, DARK_SLIME_COLOR, (decay_cell[0], decay_cell[1], 2, 2))  # Dark effect
            pygame.draw.rect(screen, SLIME_TRAIL_COLOR, (decay_cell[0], decay_cell[1], 1, 1))  # Exploring trail effect

        trail_cells.append(cell)

        if iteration % UPDATE_FREQUENCY == 0:
            pygame.display.update()

    # Draw the final optimal path if it exists
    if previous[end[1], end[0]] is not None:
        current_cell = end
        while current_cell != start:
            prev_cell = previous[current_cell[1], current_cell[0]]
            pygame.draw.line(screen, (232, 216, 67), prev_cell, current_cell, 2)
            current_cell = prev_cell
    else:
        print("No valid path exists.")


def start_button_action(screen, barrier_map):
    clear_screen(screen, barrier_map)
    get_user_barrier_input(screen, barrier_map) # Barrier drawing event
    clear_screen(screen, barrier_map)
    start, end = get_user_input(screen, barrier_map) # Start, end points input event
    pygame.draw.circle(screen, (255, 255, 255), end, 7)
    if start and end:
        draw_algorithm_steps(screen, barrier_map, start, end)
    barrier_map[:] = generate_barrier_map()

def main():
    pygame.init()
    #frames per second setting
    FPS = 30
    fpsClock = pygame.time.Clock()
    screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
    barrier_map = generate_barrier_map()

    button_rect = pygame.Rect(30, GRID_HEIGHT - 70, 100, 50)
    button_text = "Start"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    start_button_action(screen, barrier_map)

        draw_button(button_rect.x, button_rect.y, button_rect.width, button_rect.height,
                    button_text, BUTTONS_COLOR, BUTTONS_HOVER_COLOR, screen)

        pygame.display.update()

if __name__ == "__main__":
    main()

