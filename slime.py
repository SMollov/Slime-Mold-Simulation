import sys
import os
import numpy as np
import pygame
import heapq

GRID_WIDTH = 1280
GRID_HEIGHT = 720
BARRIER_FILE = 'barrier_map.npy'
UPDATE_FREQUENCY = 500 
START = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
END = (GRID_WIDTH // 8, GRID_HEIGHT // 8)
neighbor_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def clear_visited_nodes(screen, barrier_map):
    screen.fill((0, 0, 0))  # Clear the screen
    draw_map(screen, barrier_map)  # Redraw the map without visited nodes
    pygame.display.update()  # Update the display

def button(x, y, w, h, inactive, active, screen, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, inactive, (x, y, w, h))

def generate_new_map():
    barrier_array = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
    barrier_indices = np.random.choice(
        GRID_HEIGHT * GRID_WIDTH, size=int(GRID_WIDTH * GRID_HEIGHT * 0.38), replace=False
    )
    barrier_array.flat[barrier_indices] = 1
    np.save(BARRIER_FILE, barrier_array)
    return barrier_array

def draw_map(screen, barrier_map):
    barriers = np.argwhere(barrier_map == 1)
    for x, y in barriers:
        pygame.draw.rect(screen, (45, 45, 45), (y, x, 1, 1))

def dijkstra(screen, barrier_map, START, END):
    heap = []
    heapq.heappush(heap, (0, START))
    visited = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=bool)
    previous = np.full((GRID_HEIGHT, GRID_WIDTH), fill_value=float('inf'), dtype=float)
    previous[START[1], START[0]] = 0
    visited_nodes = []

    while heap:
        current_cost, current_node = heapq.heappop(heap)
        visited[current_node[1], current_node[0]] = True
        visited_nodes.append(current_node)
        if current_node == END:
            break
        
        neighbors = get_neighbors(current_node, barrier_map)
        for neighbor in neighbors:
            distance = previous[current_node[1], current_node[0]] + 1
            if distance < previous[neighbor[1], neighbor[0]]:
                previous[neighbor[1], neighbor[0]] = distance
                heapq.heappush(heap, (distance, neighbor))

    return visited_nodes

def get_neighbors(node, grid):
    x, y = node
    neighbors = [(x + dx, y + dy) for dx, dy in neighbor_offsets if 0 <= x + dx < GRID_WIDTH and 0 <= y + dy < GRID_HEIGHT and grid[y + dy, x + dx] != 1]
    return neighbors

def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
    # Draw background
    screen.fill((0,0,0))
    # Check and create barrier_map
    if os.path.exists(BARRIER_FILE):
        barrier_map = np.load(BARRIER_FILE)
    else:
        barrier_map = generate_new_map()
    text_color = (255, 248, 219)
    buttons_color = (110, 24, 24)
    buttons_hover_color = (60, 0, 15)
    buttons_font = pygame.font.SysFont("arial", 24, bold=True)
    # Create a run button
    run_button = pygame.Rect(20, GRID_HEIGHT-70, 100, 50)
    run_button_text = buttons_font.render("Run", True, text_color)
    # Create a generate map button
    gen_button = pygame.Rect(140, GRID_HEIGHT-70, 215, 50)
    gen_button_text = buttons_font.render("Generate Map", True, text_color)

    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if gen_button.collidepoint(mouse_pos):
                    barrier_map = generate_new_map()
                    clear_visited_nodes(screen, barrier_map)
                draw_map(screen, barrier_map)
                if run_button.collidepoint(mouse_pos):
                    clear_visited_nodes(screen, barrier_map)
                    draw_map(screen, barrier_map)
                    pygame.draw.circle(screen, (255, 248, 219), END, 5)
                    visited_nodes = dijkstra(screen, barrier_map, START, END)    
                    visited_color = (217, 195, 108)
                    iteration = 0
                    for node in visited_nodes:
                        pygame.draw.rect(screen, visited_color, (node[0], node[1], 1, 1))
                        iteration += 1
                        if iteration % UPDATE_FREQUENCY == 0:
                            pygame.display.update()

        # Draw the buttons
        button(run_button.x, run_button.y, run_button.width, run_button.height, buttons_color, buttons_hover_color, screen, None)
        button(gen_button.x, gen_button.y, gen_button.width, gen_button.height, buttons_color, buttons_hover_color, screen, None)
        screen.blit(run_button_text, run_button.move(25, 10))
        screen.blit(gen_button_text, gen_button.move(25, 10))
        pygame.display.update()
if __name__ == "__main__":
    main()