import math
import pygame

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (205, 205, 205)
DARK_GRAY = (155, 155, 155)
BLUE = (163, 198, 255)
RED = (255, 173, 163)

# Const
grav = 2
radius = 15
node_border = 2

# Initialize (set up system)
pygame.init()
size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Double Pendulum")
clock = pygame.time.Clock()
done = False

# For adjusting node position (setting up the nodes correctly)
started = False
init_mouse_pos = [0, 0]
init_displacement = [0, 0]

pygame.font.init()
font_type = "Times New Roman"
text_font = pygame.font.SysFont(font_type, 15)

# Default node
anchor_pt = 250
mass = 20
dist_nodes = 200
node_0_pos = [int(size[0] / 2), anchor_pt]

class Doub_Pendulum:
    # TODO: Default values
    def __init__ (self, mass_1, mass_2, len_1, len_2, color):
        self.mass_1 = mass_1
        self.mass_2 = mass_2

        self.len_1 = len_1
        self.len_2 = len_2

        self.ang_1 = 1.5
        self.ang_2 = 1.3

        self.color = color

        self.ang_vel_1 = 0
        self.ang_vel_2 = 0

        self.drag = False
        self.drag_target = 0

    def adjust_node(self):
        pos_1 = ang_to_pos(self.ang_1, node_0_pos, self.len_1)
        pos_2 = ang_to_pos(self.ang_2, pos_1, self.len_2)

        new_mouse_pos = pygame.mouse.get_pos()
        x_dist = new_mouse_pos[0] - init_mouse_pos[0]
        y_dist = new_mouse_pos[1] - init_mouse_pos[1]

        # wtf is this math
        if self.drag:
            if self.drag_target == 1:
                i = pos_1[0] + x_dist + init_displacement[0]
                j = pos_1[1] + y_dist + init_displacement[1]
                A = node_0_pos
                B = [i, j]

                magnitude = (math.sqrt(math.pow((B[0] - A[0]), 2.0) + math.pow((B[1] - A[1]), 2.0)))
                old_node_1_pos = pos_1[:]

                pos_1[0] = int(A[0] + self.len_1 * (B[0] - A[0]) / magnitude)
                pos_1[1] = int(A[1] + self.len_1 * (B[1] - A[1]) / magnitude)

                pos_2[0] += (pos_1[0] - old_node_1_pos[0])
                pos_2[1] += (pos_1[1] - old_node_1_pos[1])
                self.set_angle(pos_1, pos_2)

            elif self.drag_target == 2:
                i = pos_2[0] + x_dist + init_displacement[0]
                j = pos_2[1] + y_dist + init_displacement[1]
                A = pos_1
                B = [i, j]

                magnitude = (math.sqrt(math.pow((B[0] - A[0]), 2.0) + math.pow((B[1] - A[1]), 2.0)))

                pos_2[0] = int(A[0] + self.len_2 * (B[0] - A[0]) / magnitude)
                pos_2[1] = int(A[1] + self.len_2 * (B[1] - A[1]) / magnitude)
                self.set_angle(pos_1, pos_2)

    def set_angle(self, pos_1, pos_2):
        diff_x = pos_1[0] - node_0_pos[0]
        diff_y = pos_1[1] - node_0_pos[1]
        self.ang_1 = math.atan2(diff_x, diff_y)

        diff_x = pos_2[0] - pos_1[0]
        diff_y = pos_2[1] - pos_1[1]
        self.ang_2 = math.atan2(diff_x, diff_y)


    def check_drag_target(self):
        global init_mouse_pos
        pos_1 = ang_to_pos(self.ang_1, node_0_pos, self.len_1)
        pos_2 = ang_to_pos(self.ang_2, pos_1, self.len_2)

        self.drag = True

        if not started:
            init_mouse_pos = pygame.mouse.get_pos()

            if mouse_in_circ(pos_1):
                init_displacement[0] = pos_1[0] - node_0_pos[0]
                init_displacement[1] = pos_1[1] - node_0_pos[1]
                self.drag_target = 1
            elif mouse_in_circ(pos_2):
                init_displacement[0] = pos_2[0] - pos_1[0]
                init_displacement[1] = pos_2[1] - pos_1[1]
                self.drag_target = 2
            else:
                # No target selected
                self.drag = False

    def move(self):
        ang_1 = self.ang_1
        ang_2 = self.ang_2
        mass_1 = self.mass_1
        mass_2 = self.mass_2
        # v = rw
        ang_vel_1 = self.ang_vel_1
        ang_vel_2 = self.ang_vel_2
        len_1 = self.len_1
        len_2 = self.len_2

        # Calculate acc
        # Whew
        q_1 = -grav * (2 * mass_1 + mass_2) * math.sin(ang_1)
        q_2 = mass_2 * grav * math.sin(ang_1 - 2 * ang_2)
        q_3 = 2 * math.sin(ang_1 - ang_2) * mass_2
        q_4 = ang_vel_2 * ang_vel_2 * len_2 + ang_vel_1 * ang_vel_1 * len_1 * math.cos(ang_1 - ang_2)
        q_5 = len_1 * (2 * mass_1 + mass_2 - mass_2 * math.cos(2 * ang_1 - 2 * ang_2))
        ang_acc_1 = (q_1 - q_2 - q_3 * q_4) / q_5

        r_1 = 2 * math.sin(ang_1 - ang_2)
        r_2 = ang_vel_1 * ang_vel_1 * len_1 * (mass_1 + mass_2)
        r_3 = grav * (mass_1 + mass_2) * math.cos(ang_1)
        r_4 = ang_vel_2 * ang_vel_2 * len_2 * mass_2 * math.cos(ang_1 - ang_2)
        r_5 = len_2 * (2 * mass_1 + mass_2 - mass_2 * math.cos(2 * ang_1 - 2 * ang_2))
        ang_acc_2 = (r_1 * (r_2 + r_3 + r_4)) / r_5

        # Add to velocity
        ang_vel_1 += ang_acc_1
        ang_vel_2 += ang_acc_2

        # Add to pos
        ang_1 += ang_vel_1
        ang_2 += ang_vel_2

        # Update actual ang pos and ang_vel
        self.ang_1 = ang_1
        self.ang_2 = ang_2
        self.ang_vel_1 = ang_vel_1
        self.ang_vel_2 = ang_vel_2

    def draw(self):
        # Draw
        node_1 = ang_to_pos(self.ang_1, node_0_pos, self.len_1)
        node_2 = ang_to_pos(self.ang_2, node_1, self.len_2)

        pygame.draw.line(screen, BLACK, node_0_pos, node_1)
        pygame.draw.line(screen, BLACK, node_1, node_2)

        pygame.draw.circle(screen, WHITE, node_0_pos, 10)
        pygame.draw.circle(screen, self.color, node_1, radius)
        pygame.draw.circle(screen, self.color, node_2, radius)

        # Outlines
        pygame.draw.circle(screen, BLACK, node_0_pos, 10, node_border)
        pygame.draw.circle(screen, BLACK, node_1, radius, node_border)
        pygame.draw.circle(screen, BLACK, node_2, radius, node_border)

        # Circle guideline
        if self.drag and self.drag_target == 1:
            pygame.draw.circle(screen, DARK_GRAY, node_0_pos, self.len_1, node_border)
        elif self.drag and self.drag_target == 2:
            pygame.draw.circle(screen, DARK_GRAY, node_1, self.len_2, node_border)

def ang_to_pos(ang, orig_pt, length):
    pos_x = int(math.sin(ang) * length + orig_pt[0])
    pos_y = int(math.cos(ang) * length + orig_pt[1])
    return [pos_x, pos_y]

def run_sim(pend):
    pend.move()

def mouse_in_circ(node_pos):
    mouse_pos = pygame.mouse.get_pos()
    
    x_dist = mouse_pos[0] - node_pos[0]
    y_dist = mouse_pos[1] - node_pos[1]

    if (x_dist * x_dist) + (y_dist * y_dist) > (radius * radius):
        return False
    else:
        return True

test = Doub_Pendulum(mass, mass, dist_nodes, dist_nodes, RED)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            test.check_drag_target()
        elif event.type == pygame.MOUSEBUTTONUP:
            test.drag = False

    # Setting up
    test.adjust_node()

    # Start simulation
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_SPACE]:
        started = True

    if started:
        run_sim(test)

    # Draw & Update
    screen.fill(GRAY)
    test.draw()
    pygame.display.flip()

    # 60 FPS
    clock.tick(60)

pygame.quit()
