import sys
import os
import numpy as np
import pygame
from queue import PriorityQueue

# Constants
GRID_WIDTH = 720
GRID_HEIGHT = 720
BARRIER_PROB = 0.381966  # Barrier "density"
UPDATE_FREQUENCY = 400  # Frequency at which the algorithm steps are updated/rendered
NEIGHBOR_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Offsets to get neighboring cells
VISITED_COLOR = (230, 218, 7)  # Color for visited cells
DECAY_COLOR = (133, 123, 28)  # Color for old cells
DECAY_COLOR2 = (22, 26, 10)  # Another color for old cells
BUTTONS_COLOR = (110, 24, 24)  # Color for buttons
BUTTONS_HOVER_COLOR = (60, 0, 15)  # Color for buttons when the mouse is hovering
FONT = "arial"  # Font used for button text

# Map generation
def generate_barrier_map():
    barrier_array = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[1 - BARRIER_PROB, BARRIER_PROB])
    return barrier_array

# UI rendering
def clear_window(screen, barrier_map):
    screen.fill((0, 0, 0))
    draw_map(screen, barrier_map)
    pygame.display.update()

def draw_map(screen, barrier_map):
    barriers = np.argwhere(barrier_map == 1)
    for x, y in barriers:
        pygame.draw.rect(screen, (45, 45, 45), (y, x, 1, 1))

def draw_button(x, y, w, h, text, inactive, active, screen, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, inactive, (x, y, w, h))

    button_text = pygame.font.SysFont(FONT, 24, bold=True).render(text, True, (255, 248, 219))
    text_rect = button_text.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(button_text, text_rect)

# Algorithm
def dijkstra(screen, barrier_map, start, end):
    queue = PriorityQueue()
    queue.put((0, start))
    visited = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=bool)
    previous = np.full((GRID_HEIGHT, GRID_WIDTH), fill_value=float('inf'), dtype=float)
    previous[start[1], start[0]] = 0
    visited_cells = []
    
    while not queue.empty():
        current_cost, current_cell = queue.get()
        visited[current_cell[1], current_cell[0]] = True
        visited_cells.append(current_cell)
        if current_cell == end:
            break

        neighbors = get_neighbors(current_cell, barrier_map)
        for neighbor in neighbors:
            distance = previous[current_cell[1], current_cell[0]] + 1
            if distance < previous[neighbor[1], neighbor[0]]:
                previous[neighbor[1], neighbor[0]] = distance
                queue.put((distance, neighbor))

    return visited_cells

def get_neighbors(cell, barrier_map):
    x, y = cell
    valid_neighbors = []
    for dx, dy in NEIGHBOR_OFFSETS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and barrier_map[ny, nx] != 1:
            valid_neighbors.append((nx, ny))
    return valid_neighbors

# User input for start and end
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

    radius = 7
    if start is not None and end is not None:
        start_x, start_y = start
        barrier_map[max(0, start_y - radius):start_y + radius, max(0, start_x - radius):start_x + radius] = 0
        end_x, end_y = end
        barrier_map[max(0, end_y - radius):end_y + radius, max(0, end_x - radius):end_x + radius] = 0

    return start, end

# Path finding process visualization
def draw_algorithm_steps(screen, barrier_map, start, end):
    visited_cells = dijkstra(screen, barrier_map, start, end)
    trail_cells = []
    iteration = 0
    update_counter = 0
    update_threshold = UPDATE_FREQUENCY
    for cell in visited_cells:
        iteration += 1
        if len(trail_cells) > (iteration / 11)/3.15:
            decay_cell = trail_cells.pop(0)
            pygame.draw.rect(screen, VISITED_COLOR, (cell[0], cell[1], 2, 2))
            pygame.draw.rect(screen, DECAY_COLOR2, (decay_cell[0], decay_cell[1], 2, 2))
            pygame.draw.rect(screen, DECAY_COLOR, (decay_cell[0], decay_cell[1], 1, 1))
        else:
            rect_width = 2
        trail_cells.append(cell)

        update_counter += 1
        if update_counter >= update_threshold:
            pygame.display.update()
            update_counter = 0

def run_button_action(screen, barrier_map):
    clear_window(screen, barrier_map)
    start, end = get_user_input(screen, barrier_map)
    pygame.draw.circle(screen, (255, 255, 255), end, 7)
    if start and end:
        draw_algorithm_steps(screen, barrier_map, start, end)
    barrier_map[:] = generate_barrier_map()

# Initialize the game and handle events
def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))

    buttons = [
        {'rect': pygame.Rect(20, GRID_HEIGHT - 70, 100, 50), 'text': "Run", 'action': run_button_action}
    ]

    barrier_map = generate_barrier_map()
    clear_window(screen, barrier_map)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for button_data in buttons:
                    if button_data['rect'].collidepoint(mouse_pos):
                        action = button_data['action']
                        if action:
                            action(screen, barrier_map)

        for button_data in buttons:
            draw_button(button_data['rect'].x, button_data['rect'].y, button_data['rect'].width,
                        button_data['rect'].height,
                        button_data['text'], BUTTONS_COLOR, BUTTONS_HOVER_COLOR, screen)

        pygame.display.update()

if __name__ == "__main__":
    main()
