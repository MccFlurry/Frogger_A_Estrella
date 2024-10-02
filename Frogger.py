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

# Configuración del juego
TILE_SIZE = 30
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE

# Rana (jugador)
frog_pos = (ROWS - 1, random.randint(0, COLS - 1))  # Posición inicial (abajo en el centro)
goal_pos = (0, random.randint(0, COLS - 1))  # Meta (arriba en el centro)

# Lista de obstáculos (cada obstáculo es un diccionario con su posición y dirección)
obstacles = []
level = 1  # Nivel inicial

# Cargar imágenes
player_img = pygame.image.load("SEMANA 9/caballo.png")
player_img = pygame.transform.scale(player_img, (TILE_SIZE, TILE_SIZE))

obstacle_img = pygame.image.load("SEMANA 9/cuchillo.png")
obstacle_img = pygame.transform.scale(obstacle_img, (TILE_SIZE, TILE_SIZE))

goal_img = pygame.image.load("SEMANA 9/meta.png")
goal_img = pygame.transform.scale(goal_img, (TILE_SIZE, TILE_SIZE))

# Función para crear obstáculos
def create_obstacles():
    global obstacles
    obstacles = []
    for i in range(1, ROWS - 1, 2):  # Filas de obstáculos cada 2 filas
        direction = 1 if i % 4 == 1 else -1  # Alterna la dirección de los obstáculos
        speed = 1  # Velocidad constante ya que solo hay un nivel
        for j in range(0, COLS, 4):  # Obstáculos espaciados
            col = (j + i) % COLS if direction == 1 else (COLS - 1 - j - i) % COLS
            obstacles.append({'row': i, 'col': col, 'dir': direction, 'speed': speed})

# Función para dibujar la cuadrícula
def draw_grid(frog_pos):
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(WINDOW, WHITE, rect)
            pygame.draw.rect(WINDOW, BLACK, rect, 1)
    
    # Dibujar jugador (rana)
    WINDOW.blit(player_img, (frog_pos[1] * TILE_SIZE, frog_pos[0] * TILE_SIZE))

    # Dibujar meta
    WINDOW.blit(goal_img, (goal_pos[1] * TILE_SIZE, goal_pos[0] * TILE_SIZE))

    # Dibujar obstáculos
    for obs in obstacles:
        WINDOW.blit(obstacle_img, (obs['col'] * TILE_SIZE, obs['row'] * TILE_SIZE))

# Función para mover los obstáculos
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
    heap = []
    heapq.heappush(heap, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while heap:
        current = heapq.heappop(heap)[1]

        if current == goal:
            break

        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            next_node = (current[0] + dx, current[1] + dy)
            if 0 <= next_node[0] < ROWS and 0 <= next_node[1] < COLS:
                if game_map[next_node[0]][next_node[1]] == 1:
                    continue  # Es un obstáculo
                new_cost = cost_so_far[current] + 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + heuristic(goal, next_node)
                    heapq.heappush(heap, (priority, next_node))
                    came_from[next_node] = current
    else:
        return None  # No se encontró camino

    # Reconstruir el camino
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

# Función principal del juego
def main():
    create_obstacles()  # Crear los obstáculos una vez
    clock = pygame.time.Clock()
    run = True
    frog_pos_current = frog_pos

    while run:
        clock.tick(5)  # Controla la velocidad del juego

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        game_map = get_game_map()

        # Calcular el camino utilizando A*
        path = a_star_search(frog_pos_current, goal_pos, game_map)

        if path is None:
            print("No se encontró un camino a la meta.")
            run = False
        else:
            for position in path:
                # Mover la rana a la siguiente posición
                frog_pos_current = position

                # Actualizar obstáculos y mapa
                move_obstacles()
                game_map = get_game_map()

                # Si hay un obstáculo en la posición de la rana, termina el juego
                if game_map[position[0]][position[1]] == 1:
                    print("El caballo ha sido golpeado por un obstáculo.")
                    run = False
                    break

                # Dibujar en pantalla
                WINDOW.fill(WHITE)
                draw_grid(frog_pos_current)
                pygame.display.update()
                clock.tick(10)

                # Si la rana llega a la meta
                if position == goal_pos:
                    print("¡El caballo ha llegado a la meta!")
                    run = False
                    break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
