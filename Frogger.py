import pygame
import heapq
import sys
import random

# Inicializamos pygame
pygame.init()

# Configuración de la ventana
WIDTH, HEIGHT = 1300, 1300  # Ventana más grande
WINDOW = pygame.display.set_mode((WIDTH + 50, HEIGHT + 50))  # Espacio extra para etiquetas
pygame.display.set_caption("Frogger con A* Optimizado")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Configuración del juego
TILE_SIZE = 45  # Ajustamos el tamaño de las celdas
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE

# Posiciones iniciales
frog_pos = (ROWS - 1, random.randint(0, COLS - 1))  # Inicio (abajo)
goal_pos = (0, random.randint(0, COLS - 1))  # Meta (arriba)

# Lista de obstáculos y nivel
obstacles = []
level = 1

# Fuentes para las etiquetas
FONT = pygame.font.SysFont('Arial', 20)

# Cargar imágenes
player_img = pygame.transform.scale(pygame.image.load("caballo.png"), (TILE_SIZE, TILE_SIZE))
obstacle_img = pygame.transform.scale(pygame.image.load("cuchillo.png"), (TILE_SIZE, TILE_SIZE))
goal_img = pygame.transform.scale(pygame.image.load("meta.png"), (TILE_SIZE, TILE_SIZE))

# Crear obstáculos
def create_obstacles():
    global obstacles
    obstacles = []
    for i in range(1, ROWS - 1, 2):
        direction = 1 if i % 4 == 1 else -1
        for j in range(0, COLS, 4):
            col = (j + i) % COLS if direction == 1 else (COLS - 1 - j - i) % COLS
            obstacles.append({'row': i, 'col': col, 'dir': direction, 'speed': 1})

def move_obstacles():
    for obs in obstacles:
        obs['col'] = (obs['col'] + obs['dir'] * obs['speed']) % COLS

# Generar mapa con penalización por cercanía a obstáculos
def get_game_map():
    game_map = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    for obs in obstacles:
        game_map[obs['row']][obs['col']] = 1
        add_obstacle_penalty(game_map, obs['row'], obs['col'])
    return game_map

def add_obstacle_penalty(game_map, row, col):
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        adj_row, adj_col = row + dx, col + dy
        if 0 <= adj_row < ROWS and 0 <= adj_col < COLS and game_map[adj_row][adj_col] != 1:
            game_map[adj_row][adj_col] = 2

def heuristic(a, b, game_map):
    distance = abs(a[0] - b[0]) + abs(a[1] - b[1])
    penalty = 5 if game_map[a[0]][a[1]] == 2 else 0
    return distance + penalty

def get_cell_name(row, col):
    return f"{chr(65 + row)}{col + 1}"

# Algoritmo A* con mensajes detallados en consola
def a_star_search(start, goal, game_map):
    heap = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}

    print(f"Inicio de A* desde {get_cell_name(*start)} hacia {get_cell_name(*goal)}")

    while heap:
        _, current = heapq.heappop(heap)
        print(f"\nExplorando nodo: {get_cell_name(*current)}")

        if current == goal:
            print("¡Meta alcanzada!\n")
            return reconstruct_path(came_from, start, goal)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_node = (current[0] + dx, current[1] + dy)

            if is_valid_node(next_node, game_map):
                new_cost = cost_so_far[current] + (1 if game_map[next_node[0]][next_node[1]] == 0 else 2)
                print(f"Evaluando vecino {get_cell_name(*next_node)} con costo {new_cost}")

                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + heuristic(next_node, goal, game_map)
                    heapq.heappush(heap, (priority, next_node))
                    came_from[next_node] = current
                    print(f"Actualizado: {get_cell_name(*next_node)} con prioridad {priority}")

    print("No se encontró un camino a la meta.")
    return None

def is_valid_node(node, game_map):
    return 0 <= node[0] < ROWS and 0 <= node[1] < COLS and game_map[node[0]][node[1]] != 1

def reconstruct_path(came_from, start, goal):
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    print(f"Ruta encontrada: {[get_cell_name(*p) for p in path]}")
    return path

def draw_grid(frog_pos, path=None):
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * TILE_SIZE + 50, row * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(WINDOW, WHITE, rect)
            pygame.draw.rect(WINDOW, BLACK, rect, 1)

    # Dibujar etiquetas de filas y columnas
    for i in range(ROWS):
        label = FONT.render(chr(65 + i), True, BLACK)
        WINDOW.blit(label, (10, i * TILE_SIZE + 60))

    for j in range(COLS):
        label = FONT.render(str(j + 1), True, BLACK)
        WINDOW.blit(label, (j * TILE_SIZE + 60, 10))

    WINDOW.blit(player_img, (frog_pos[1] * TILE_SIZE + 50, frog_pos[0] * TILE_SIZE + 50))
    WINDOW.blit(goal_img, (goal_pos[1] * TILE_SIZE + 50, goal_pos[0] * TILE_SIZE + 50))

    for obs in obstacles:
        WINDOW.blit(obstacle_img, (obs['col'] * TILE_SIZE + 50, obs['row'] * TILE_SIZE + 50))

    if path:
        for i in range(len(path) - 1):
            start, end = path[i], path[i + 1]
            pygame.draw.line(WINDOW, RED, 
                             (start[1] * TILE_SIZE + TILE_SIZE // 2 + 50, start[0] * TILE_SIZE + TILE_SIZE // 2 + 50),
                             (end[1] * TILE_SIZE + TILE_SIZE // 2 + 50, end[0] * TILE_SIZE + TILE_SIZE // 2 + 50), 3)

def main():
    create_obstacles()
    clock = pygame.time.Clock()
    frog_pos_current = frog_pos
    path = None

    run = True
    while run:
        clock.tick(5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        move_obstacles()
        game_map = get_game_map()

        # Verificamos si no hay camino o si el camino no llega a la meta
        if path is None or (len(path) > 0 and path[-1] != goal_pos):
            path = a_star_search(frog_pos_current, goal_pos, game_map)

            if path is None:
                print("No se encontró un camino válido.")
                run = False  # Puedes decidir si quieres terminar el juego aquí

        if path and len(path) > 0:
            frog_pos_current = path.pop(0)
            if frog_pos_current == goal_pos:
                print("¡El caballo ha llegado a la meta!")

        WINDOW.fill(WHITE)
        draw_grid(frog_pos_current, path)
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
