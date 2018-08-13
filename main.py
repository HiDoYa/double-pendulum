import math
import pygame

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (205, 205, 205)
BLUE = (163, 198, 255)
RED = (255, 173, 163)

# Const
grav = 9.8
radius = 20
node_border = 2

# Initialize
pygame.init()
size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Double Pendulum")
done = False

# For before_start (setting up the nodes correctly)
started = False
drag = False
drag_target = 0
init_mouse_pos = [0, 0]

dist_nodes = 200

pygame.font.init()
font_type = "Times New Roman"
text_font = pygame.font.SysFont(font_type, 15)

node_0_pos = [640, 250]
node_1_pos = [640, 450]
node_2_pos = [640, 650]

clock = pygame.time.Clock()

def mouse_in_circ(node_pos):
    mouse_pos = pygame.mouse.get_pos()
    
    x_dist = mouse_pos[0] - node_pos[0]
    y_dist = mouse_pos[1] - node_pos[1]

    if (x_dist * x_dist) + (y_dist * y_dist) > (radius * radius):
        return False
    else:
        return True

def check_drag_target():
    global started
    global drag
    global init_mouse_pos
    global drag_target
    global node_1_pos
    global node_2_pos

    if not started and drag:
        init_mouse_pos = pygame.mouse.get_pos()

        if mouse_in_circ(node_1_pos):
            drag_target = 1
        elif mouse_in_circ(node_2_pos):
            drag_target = 2
        else:
            # No target selected
            drag = False

def before_start():
    global new_mouse_pos
    global node_1_pos
    global dist_nodes

    new_mouse_pos = pygame.mouse.get_pos()
    x_dist = new_mouse_pos[0] - init_mouse_pos[0]
    y_dist = new_mouse_pos[1] - init_mouse_pos[1]

    # wtf is this math
    if drag and drag_target == 1:
        i = node_1_pos[0] + x_dist
        j = node_1_pos[1] + y_dist + node_0_pos[1]

        A = node_0_pos
        B = [i, j]

        magnitude = (math.sqrt(math.pow((B[0] - A[0]), 2.0) + math.pow((B[1] - A[1]), 2.0)))

        node_1_pos[0] = int(A[0] + dist_nodes * (B[0] - A[0]) / magnitude)
        node_1_pos[1] = int(A[1] + dist_nodes * (B[1] - A[1]) / magnitude)
    elif drag_target == 2:
        i = node_2_pos[0] + x_dist
        j = node_2_pos[1] + y_dist + node_0_pos[1]

        A = node_1_pos
        B = [i, j]

        magnitude = (math.sqrt(math.pow((B[0] - A[0]), 2.0) + math.pow((B[1] - A[1]), 2.0)))

        node_2_pos[0] = int(A[0] + dist_nodes * (B[0] - A[0]) / magnitude)
        node_2_pos[1] = int(A[1] + dist_nodes * (B[1] - A[1]) / magnitude)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            drag = True
            check_drag_target()
        elif event.type == pygame.MOUSEBUTTONUP:
            drag = False

    before_start()
    screen.fill(GRAY)


    pygame.draw.line(screen, BLACK, node_0_pos, node_1_pos)
    pygame.draw.line(screen, BLACK, node_1_pos, node_2_pos)

    pygame.draw.circle(screen, WHITE, node_0_pos, 10)
    pygame.draw.circle(screen, BLUE, node_1_pos, radius)
    pygame.draw.circle(screen, RED, node_2_pos, radius)

    # Outlines
    pygame.draw.circle(screen, BLACK, node_0_pos, 10, node_border)
    pygame.draw.circle(screen, BLACK, node_1_pos, radius, node_border)
    pygame.draw.circle(screen, BLACK, node_2_pos, radius, node_border)

    # TODO
    pygame.draw.circle(screen, BLACK, node_0_pos, dist_nodes, node_border)

    # Update
    pygame.display.flip()

    # 60 FPS
    clock.tick(60)

pygame.quit()
