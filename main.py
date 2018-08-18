import math
import pygame

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (205, 205, 205)
DARK_GRAY = (155, 155, 155)
GREEN_TEXT = (2, 130, 74)
RED_TEXT = (147, 33, 7)

# Pendulum colors
RED = (255, 173, 163)
D_RED = (RED[0] - 50, RED[1] - 50, RED[2] - 50)
BLUE = (163, 198, 255)
D_BLUE = (BLUE[0] - 50, BLUE[1] - 50, BLUE[2] - 50)
GREEN = (101, 242, 104)
D_GREEN = (GREEN[0] - 50, GREEN[1] - 50, GREEN[2] - 50)

# Const
grav = 1
radius = 15
node_border = 2

# Initialize (set up system)
pygame.init()
size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Double Pendulum")
clock = pygame.time.Clock()
done = False
time_pass = 0;
keep_draw = True
disp_error_text = False
error_time = 90

pend_list = [True, False, False]
cur_pend_select = 0;

# For adjusting node position (setting up the nodes correctly)
started = False
init_mouse_pos = [0, 0]
init_displacement = [0, 0]

pygame.font.init()
font_type = "Times New Roman"
text_font = pygame.font.SysFont(font_type, 15)

# Default node
anchor_pt = 250
mass = 200
dist_nodes = 200
node_0_pos = [int(size[0] / 2), anchor_pt]

class Doub_Pendulum:
    # TODO: Default values
    def __init__ (self, mass_1, mass_2, len_1, len_2, color, color_path):
        self.mass_1 = mass_1
        self.mass_2 = mass_2

        self.len_1 = len_1
        self.len_2 = len_2

        self.ang_1 = 0
        self.ang_2 = 0

        self.old_path = []

        self.color = color
        self.color_path = color_path

        self.ang_vel_1 = 0
        self.ang_vel_2 = 0

        self.drag = False
        self.drag_target = 0

    def reset(self):
        self.ang_1 = 0
        self.ang_2 = 0
        self.ang_vel_1 = 0
        self.ang_vel_2 = 0
        self.old_path.clear()

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
                self.set_angle_1(pos_1, pos_2)

            elif self.drag_target == 2:
                i = pos_2[0] + x_dist + init_displacement[0]
                j = pos_2[1] + y_dist + init_displacement[1]
                A = pos_1
                B = [i, j]

                magnitude = (math.sqrt(math.pow((B[0] - A[0]), 2.0) + math.pow((B[1] - A[1]), 2.0)))

                pos_2[0] = int(A[0] + self.len_2 * (B[0] - A[0]) / magnitude)
                pos_2[1] = int(A[1] + self.len_2 * (B[1] - A[1]) / magnitude)
                self.set_angle_2(pos_1, pos_2)

    def set_angle_1(self, pos_1, pos_2):
        diff_x = pos_1[0] - node_0_pos[0]
        diff_y = pos_1[1] - node_0_pos[1]
        self.ang_1 = math.atan2(diff_x, diff_y)

    def set_angle_2(self, pos_1, pos_2):
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
        global error_time
        global disp_error_text
        try:
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
        except ValueError:
            error_time = 0
            disp_error_text = True

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

    def draw_path(self):
        node_1 = ang_to_pos(self.ang_1, node_0_pos, self.len_1)
        node_2 = ang_to_pos(self.ang_2, node_1, self.len_2)
        
        # Create path
        if started:
            self.old_path.append(node_2[:])

            if len(self.old_path) > 10 and not keep_draw:
                self.old_path.pop(0)

            for i in range(0, len(self.old_path)):
                if i != 0:
                    pygame.draw.line(screen, self.color_path, self.old_path[i], self.old_path[i - 1], 3)


def reset_old_paths(pend_0, pend_1, pend_2):
    pend_0.old_path.clear()
    pend_1.old_path.clear()
    pend_2.old_path.clear()

def run_sim(pend_0, pend_1, pend_2, pend_list):
    pend_0.move()
    if pend_list[1]:
        pend_1.move()
    if pend_list[2]:
        pend_2.move()

def draw(pend_0, pend_1, pend_2, pend_list):

    # Draw paths first then nodes
    if cur_pend_select == 0:
        if pend_list[1]:
            pend_1.draw_path()
        if pend_list[2]:
            pend_2.draw_path()
        pend_0.draw_path()

        if pend_list[1]:
            pend_1.draw()
        if pend_list[2]:
            pend_2.draw()
        pend_0.draw()
    elif cur_pend_select == 1:
        if pend_list[2]:
            pend_2.draw_path()
        pend_0.draw_path()
        if pend_list[1]:
            pend_1.draw_path()

        if pend_list[2]:
            pend_2.draw()
        pend_0.draw()
        if pend_list[1]:
            pend_1.draw()
    elif cur_pend_select == 2:
        pend_0.draw_path()
        if pend_list[1]:
            pend_1.draw_path()
        if pend_list[2]:
            pend_2.draw_path()

        pend_0.draw()
        if pend_list[1]:
            pend_1.draw()
        if pend_list[2]:
            pend_2.draw()

def ang_to_pos(ang, orig_pt, length):
    global disp_error_text
    global error_time
    try:
        pos_x = int(math.sin(ang) * length + orig_pt[0])
        pos_y = int(math.cos(ang) * length + orig_pt[1])
    except ValueError:
        pos_x = 0
        pos_y = 0
        error_time = 0
        disp_error_text = True

    return [pos_x, pos_y]

def mouse_in_circ(node_pos):
    mouse_pos = pygame.mouse.get_pos()
    
    x_dist = mouse_pos[0] - node_pos[0]
    y_dist = mouse_pos[1] - node_pos[1]

    if (x_dist * x_dist) + (y_dist * y_dist) > (radius * radius):
        return False
    else:
        return True

def reset_all(pend_0, pend_1, pend_2):
    pend_0.reset()
    pend_1.reset()
    pend_2.reset()

# Instructions
text = pygame.font.SysFont("Gill Sans", 25)
text_instr_0 = text.render("Press r to restart", False, BLACK)
text_instr_1 = text.render("Press 1, 2, or 3 to select a different pendulum", False, BLACK)
text_instr_2 = text.render("Press s to change the path option", False, BLACK)
text_instr_3 = text.render("Currently selected pendulum: ", False, BLACK)

l_text = pygame.font.SysFont("Gill Sans", 30)
text_instr_start = l_text.render("Press space to start the pendulum", False, GREEN_TEXT)
text_instr_stop = l_text.render("Press space to stop the pendulum", False, RED_TEXT)

text_instr_r = text.render("Red", False, D_RED)
text_instr_g = text.render("Green", False, D_GREEN)
text_instr_b = text.render("Blue", False, D_BLUE)

text_error = text.render("Error: Pendulum going too fast", False, BLACK)

def draw_instr():
    global error_time
    global started

    screen.blit(text_instr_0, (30, 10))
    screen.blit(text_instr_1, (30, 45))
    screen.blit(text_instr_2, (30, 80))
    screen.blit(text_instr_3, (900, 10))

    if started:
        screen.blit(text_instr_stop, (30, 650))
    else:
        screen.blit(text_instr_start, (30, 650))

    if cur_pend_select == 0:
        screen.blit(text_instr_r, (1210, 10))
    elif cur_pend_select == 1:
        screen.blit(text_instr_g, (1210, 10))
    elif cur_pend_select == 2:
        screen.blit(text_instr_b, (1210, 10))

    error_time += 1;
    if disp_error_text and error_time < 90:
        reset_all(pend_0, pend_1, pend_2)
        started = False
        screen.blit(text_error, (400, 500))


# 3 pendulums max
pend_0 = Doub_Pendulum(mass, mass, dist_nodes, dist_nodes, RED, D_RED)
pend_1 = Doub_Pendulum(mass, mass, dist_nodes, dist_nodes, GREEN, D_GREEN)
pend_2 = Doub_Pendulum(mass, mass, dist_nodes, dist_nodes, BLUE, D_BLUE)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if cur_pend_select == 0:
                pend_0.check_drag_target()
            elif cur_pend_select == 1:
                pend_1.check_drag_target()
            elif cur_pend_select == 2:
                pend_2.check_drag_target()
        elif event.type == pygame.MOUSEBUTTONUP:
            if cur_pend_select == 0:
                pend_0.drag = False
            elif cur_pend_select == 1:
                pend_1.drag = False
            elif cur_pend_select == 2:
                pend_2.drag = False
            
    pressed = pygame.key.get_pressed()

    # Setting up pendulums
    if pressed[pygame.K_1] and time_pass > 20:
        cur_pend_select = 0
        time_pass = 0
    if pressed[pygame.K_2] and time_pass > 20:
        pend_list[1] = True
        cur_pend_select = 1
        time_pass = 0
    if pressed[pygame.K_3] and time_pass > 20:
        pend_list[2] = True
        cur_pend_select = 2
        time_pass = 0

    if pressed[pygame.K_a] and not started and time_pass > 20:
        keep_draw = not keep_draw
        time_pass = 0

    if pressed[pygame.K_r] and time_pass > 20:
        time_pass = 0
        started = False
        reset_all(pend_0, pend_1, pend_2)

    if pressed[pygame.K_s] and time_pass > 20:
        time_pass = 0
        keep_draw = not keep_draw

    # The actual adjustment
    if cur_pend_select == 0:
        pend_0.adjust_node()
    elif cur_pend_select == 1:
        pend_1.adjust_node()
    elif cur_pend_select == 2:
        pend_2.adjust_node()

    # Start simulation
    time_pass += 1;
    if pressed[pygame.K_SPACE] and not started and time_pass > 20:
        time_pass = 0
        started = True
    elif pressed[pygame.K_SPACE] and started and time_pass > 20:
        time_pass = 0
        started = False
        reset_old_paths(pend_0, pend_1, pend_2)


    if started:
        run_sim(pend_0, pend_1, pend_2, pend_list)

    # Draw & Update
    screen.fill(GRAY)
    draw(pend_0, pend_1, pend_2, pend_list)
    draw_instr()
    pygame.display.flip()

    # 60 FPS
    clock.tick(60)

pygame.quit()
