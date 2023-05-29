import sys
import os
import numpy as np
import pygame
import heapq

GRID_WIDTH = 1280
GRID_HEIGHT = 720
BARRIER_FILE = 'barrier_map.npy'
UPDATE_FREQUENCY = 1000
START = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
END = (GRID_WIDTH // 8, GRID_HEIGHT // 8)

def create_barrier_array():
    # Check if the barrier map file exists
    if os.path.exists(BARRIER_FILE):
        barrier_array = np.load(BARRIER_FILE)
    else:
        # Generate random barrier array
        barrier_array = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
        barrier_indices = np.random.choice(GRID_HEIGHT * GRID_WIDTH, size=int(GRID_WIDTH * GRID_HEIGHT * 0.36), replace=False)
        barrier_array.flat[barrier_indices] = 1

        # Save the barrier array to a file
        np.save(BARRIER_FILE, barrier_array)

    return barrier_array


def dijkstra(screen, barrier_map, START, END):
    heap = []
    heapq.heappush(heap, (0, START))
    visited = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=bool)
    previous = np.full((GRID_HEIGHT, GRID_WIDTH), fill_value=float('inf'), dtype=float)
    previous[START[1], START[0]] = 0

    iteration = 0
    while heap:
        current_cost, current_node = heapq.heappop(heap)

        if current_node == END:
            break
        
        visited[current_node[1], current_node[0]] = True
        pygame.draw.rect(screen, (219, 185, 51), (current_node[0], current_node[1], 1, 1))
        neighbors = get_neighbors(current_node, barrier_map)

        for neighbor in neighbors:
            distance = previous[current_node[1], current_node[0]] + 1

            if distance < previous[neighbor[1], neighbor[0]]:
                previous[neighbor[1], neighbor[0]] = distance
                heapq.heappush(heap, (distance, neighbor))

        iteration += 1
        if iteration % UPDATE_FREQUENCY == 0:
            pygame.display.update()

    return previous  

neighbor_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

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

    # Draw the barrier_map
    barrier_map = create_barrier_array()
    barriers = np.argwhere(barrier_map == 1)
    for x, y in barriers:
        pygame.draw.rect(screen, (45, 45, 45), (x, y, 1, 1))
    
    # Draw the target point
    pygame.draw.circle(screen, ((234, 221, 189)), (END[0], END[1]), 5)

    dijkstra(screen, barrier_map, START, END)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()                                 
                                      
if __name__ == "__main__":
    main()

