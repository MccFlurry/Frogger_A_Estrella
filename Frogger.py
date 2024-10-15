import pygame
import heapq
import sys
import random

# Inicializamos pygame
pygame.init()

# Configuración de la ventana
WIDTH, HEIGHT = 600, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Frogger con A*")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Configuración del juego
TILE_SIZE = 30
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE

# caballo (jugador)
frog_pos = (ROWS - 1, random.randint(0, COLS - 1))  # Posición inicial (abajo)
goal_pos = (0, random.randint(0, COLS - 1))  # Meta (arriba)

# Lista de obstáculos (cada obstáculo es un diccionario con su posición y dirección)
obstacles = []
level = 1  # Nivel inicial

# Cargar imágenes
player_img = pygame.image.load("caballo.png")
player_img = pygame.transform.scale(player_img, (TILE_SIZE, TILE_SIZE))

obstacle_img = pygame.image.load("cuchillo.png")
obstacle_img = pygame.transform.scale(obstacle_img, (TILE_SIZE, TILE_SIZE))

goal_img = pygame.image.load("meta.png")
goal_img = pygame.transform.scale(goal_img, (TILE_SIZE, TILE_SIZE))

# Convertir posiciones a letras (A1, B2, etc.)
def get_cell_name(row, col):
    return chr(65 + row) + str(col + 1)

# Crear y mover obstáculos
def create_obstacles():
    global obstacles
    obstacles = []
    for i in range(1, ROWS - 1, 2):  # Filas de obstáculos cada 2 filas
        direction = 1 if i % 4 == 1 else -1  # Alterna la dirección de los obstáculos
        speed = 1  # Velocidad constante ya que solo hay un nivel
        for j in range(0, COLS, 4):  # Obstáculos espaciados
            col = (j + i) % COLS if direction == 1 else (COLS - 1 - j - i) % COLS
            obstacles.append({'row': i, 'col': col, 'dir': direction, 'speed': speed})

def move_obstacles():
    for obs in obstacles:
        obs['col'] += obs['dir'] * obs['speed']
        if obs['col'] < 0:
            obs['col'] = COLS - 1
        elif obs['col'] >= COLS:
            obs['col'] = 0

# Generar mapa del juego
def get_game_map():
    game_map = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    for obs in obstacles:
        game_map[obs['row']][obs['col']] = 1  # 1 representa un obstáculo
    return game_map

# Heurística para A* (distancia de Manhattan)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Algoritmo A*
def a_star_search(start, goal, game_map):
    heap = initialize_heap(start)
    came_from, cost_so_far = initialize_costs(start)

    while heap:
        current = heapq.heappop(heap)[1]

        if current == goal:
            break

        process_neighbors(current, goal, game_map, heap, came_from, cost_so_far)
    else:
        return None  # No se encontró camino

    return reconstruct_path(came_from, start, goal)

def initialize_heap(start):
    heap = []
    heapq.heappush(heap, (0, start))
    return heap

def initialize_costs(start):
    came_from = {start: None}
    cost_so_far = {start: 0}
    return came_from, cost_so_far

def process_neighbors(current, goal, game_map, heap, came_from, cost_so_far):
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        next_node = (current[0] + dx, current[1] + dy)
        if is_valid_node(next_node, game_map):
            new_cost = cost_so_far[current] + 1
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                update_costs(next_node, new_cost, goal, heap, came_from, cost_so_far, current)

def is_valid_node(node, game_map):
    return 0 <= node[0] < ROWS and 0 <= node[1] < COLS and game_map[node[0]][node[1]] != 1

def update_costs(next_node, new_cost, goal, heap, came_from, cost_so_far, current):
    cost_so_far[next_node] = new_cost
    priority = new_cost + heuristic(goal, next_node)
    heapq.heappush(heap, (priority, next_node))
    came_from[next_node] = current

def reconstruct_path(came_from, start, goal):
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

# Dibujar la cuadrícula y los elementos del juego
def draw_grid(frog_pos, path=None):
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(WINDOW, WHITE, rect)
            pygame.draw.rect(WINDOW, BLACK, rect, 1)
    
    # Dibujar jugador (caballo)
    WINDOW.blit(player_img, (frog_pos[1] * TILE_SIZE, frog_pos[0] * TILE_SIZE))

    # Dibujar meta
    WINDOW.blit(goal_img, (goal_pos[1] * TILE_SIZE, goal_pos[0] * TILE_SIZE))

    # Dibujar obstáculos
    for obs in obstacles:
        WINDOW.blit(obstacle_img, (obs['col'] * TILE_SIZE, obs['row'] * TILE_SIZE))

    # Dibujar flechas del camino
    if path:
        for i in range(len(path) - 1):
            start = path[i]
            end = path[i + 1]
            start_x = start[1] * TILE_SIZE + TILE_SIZE // 2
            start_y = start[0] * TILE_SIZE + TILE_SIZE // 2
            end_x = end[1] * TILE_SIZE + TILE_SIZE // 2
            end_y = end[0] * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.line(WINDOW, RED, (start_x, start_y), (end_x, end_y), 3)

# Función principal del juego
def main():
    create_obstacles()  # Crear los obstáculos una vez
    clock = pygame.time.Clock()
    run = True
    frog_pos_current = frog_pos
    game_over = False  # Bandera para indicar si el juego ha terminado

    while run:
        clock.tick(5)  # Controla la velocidad del juego

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Solo continuar si el juego no ha terminado
        if not game_over:
            game_map = get_game_map()

            # Calcular el camino utilizando A*
            path = a_star_search(frog_pos_current, goal_pos, game_map)

            if path is None:
                print("No se encontró un camino a la meta.")
                WINDOW.fill(WHITE)
                draw_grid(frog_pos_current)
                pygame.display.update()
                continue  # Mantener la ventana abierta, pero sin movimiento adicional

            for position in path:
                # Mostrar en la terminal el movimiento del caballo
                current_cell = get_cell_name(frog_pos_current[0], frog_pos_current[1])
                next_cell = get_cell_name(position[0], position[1])
                print(f"Caballo se mueve de {current_cell} a {next_cell}")

                # Mover el caballo a la siguiente posición
                frog_pos_current = position

                # Actualizar obstáculos y mapa
                move_obstacles()
                game_map = get_game_map()

                # Si hay un obstáculo en la posición de el caballo, termina el movimiento y el juego
                if game_map[position[0]][position[1]] == 1:
                    print("El caballo ha sido golpeado por un obstáculo.")
                    WINDOW.fill(WHITE)
                    draw_grid(frog_pos_current)
                    pygame.display.update()
                    game_over = True  # Establecer la bandera de que el juego ha terminado
                    break

                # Dibujar en pantalla
                WINDOW.fill(WHITE)
                draw_grid(frog_pos_current, path=path)
                pygame.display.update()
                clock.tick(10)

                # Si el caballo llega a la meta
                if position == goal_pos:
                    print("¡El caballo ha llegado a la meta!")
                    game_over = True  # Establecer la bandera de que el juego ha terminado
                    break

        # Si el juego ha terminado, mantener la pantalla abierta sin permitir más movimientos
        else:
            WINDOW.fill(WHITE)
            draw_grid(frog_pos_current)
            pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
