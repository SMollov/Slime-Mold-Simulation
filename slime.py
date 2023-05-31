import sys
import os
import numpy as np
import pygame
import heapq

#TO DO - Irregular growth pulses, Veins, Texture, Custom Barriers

GRID_WIDTH = 1280
GRID_HEIGHT = 720
BARRIER_PROB = 0.385
UPDATE_FREQUENCY = 200
NEIGHBOR_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
VISITED_COLOR = (230, 218, 7)
DECAY_COLOR = (138, 143, 19)
DECAY_COLOR2 = (22, 26, 10)
buttons_color = (110, 24, 24)
buttons_hover_color = (60, 0, 15)
font = "arial"

def generate_new_map():
    barrier_array = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[1 - BARRIER_PROB, BARRIER_PROB])
    return barrier_array

def clear_window(screen, barrier_map):
    screen.fill((0, 0, 0))
    draw_map((screen), barrier_map)
    pygame.display.update()

def draw_map(screen, barrier_map):
    barriers = np.argwhere(barrier_map == 1)
    for x, y in barriers:
        pygame.draw.rect(screen, (45, 45, 45), (y, x, 1, 1))


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
            pygame.draw.circle(screen, (255, 0, 0), end, 7)
        pygame.display.update()

    radius = 7
    if start is not None and end is not None:
        start_x, start_y = start
        barrier_map[max(0, start_y - radius):start_y + radius, max(0, start_x - radius):start_x + radius] = 0
        end_x, end_y = end
        barrier_map[max(0, end_y - radius):end_y + radius, max(0, end_x - radius):end_x + radius] = 0

    return start, end

def dijkstra(screen, barrier_map, start, end):
    heap = []
    heapq.heappush(heap, (0, start))
    visited = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=bool)
    previous = np.full((GRID_HEIGHT, GRID_WIDTH), fill_value=float('inf'), dtype=float)
    previous[start[1], start[0]] = 0
    visited_nodes = []

    while heap:
        current_cost, current_node = heapq.heappop(heap)
        visited[current_node[1], current_node[0]] = True
        visited_nodes.append(current_node)
        if current_node == end:
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
    neighbors = [(x + dx, y + dy) for dx, dy in NEIGHBOR_OFFSETS if 0 <= x + dx < GRID_WIDTH and 0 <= y + dy < GRID_HEIGHT and grid[y + dy, x + dx] != 1]
    return neighbors

def button(x, y, w, h, inactive, active, screen, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, inactive, (x, y, w, h))

def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))  
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if run_button.collidepoint(mouse_pos):
                    barrier_map = generate_new_map()
                    clear_window(screen, barrier_map)
                    start, end = get_user_input(screen, barrier_map)
                    visited_nodes = dijkstra(screen, barrier_map, start, end)    
                    trail_nodes = []
                    iteration = 0
                    for node in visited_nodes:
                        iteration += 1    
                                           
                        if len(trail_nodes) > iteration/12:
                            decay_node = trail_nodes.pop(0)
                            pygame.draw.rect(screen, VISITED_COLOR, (node[0], node[1], 2,2)) 
                            pygame.draw.rect(screen, DECAY_COLOR2, (decay_node[0], decay_node[1], 2, 2))
                            pygame.draw.rect(screen, DECAY_COLOR, (decay_node[0], decay_node[1], 1, 1))

                        else:
                            rect_width = 2
                        trail_nodes.append(node)
                        
                        if iteration % UPDATE_FREQUENCY == 0:
                            pygame.display.update()

        
        buttons_font = pygame.font.SysFont(font, 24, bold=True)
        text_font = pygame.font.SysFont(font, 20)
        run_button = pygame.Rect(20, GRID_HEIGHT-70, 100, 50)
        run_button_text = buttons_font.render("Run", True, (255, 248, 219))
        button(run_button.x, run_button.y, run_button.width, run_button.height, buttons_color, buttons_hover_color, screen, None)
        screen.blit(run_button_text, run_button.move(25, 10))
        start_text = text_font.render("Press Run and click to add start and end points.", True, (255, 248, 219))
        screen.blit(start_text, (0,0))

        pygame.display.update()

if __name__ == "__main__":
    main()