import math  # For complex mathematical operations
import pygame  # For game development
import pymunk  # For physics simulation
import pymunk.pygame_util  # For easier integration of Pymunk with Pygame
import sys  # For system operations like exiting
import threading  # For handling the timer

# Initialize Pygame and set up the display
pygame.init()
HEIGHT = 640
WIDTH = 1200
window = pygame.display.set_mode((WIDTH, HEIGHT ))
pygame.display.set_caption("Tamer's Pool Quest")

# Create a clock object to manage the frame rate
clock = pygame.time.Clock()
FPS = 60
Lily = 36
shoot = True
force = 0
power = False
hole_width = 66
well = []
message_counter = 0  # Counter for the number of balls pocketed
display_message = ''  # Message to display

# Load images
cane = pygame.image.load('images/cue.png').convert_alpha()
table = pygame.image.load('images/table (2).png').convert_alpha()
ball_picture = [pygame.image.load(f'images/ball_{Milo}.png').convert_alpha() for Milo in range(1, 17)]

# Load font
font = pygame.font.Font(None, 60)

# Load sound
collision_sound = pygame.mixer.Sound('billiards+2.wav')

# Create a Pymunk space for the physics simulation
space = pymunk.Space()
static_body = space.static_body


def create_ball(radius, pos):
    """
    Function to create a ball with a given radius and position.
    """
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.mass = 5
    shape.elasticity = 0.8
    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot.max_bias = 0
    pivot.max_force = 1000
    space.add(body, shape, pivot)
    return body, shape

# Create the cue ball
new_ball_body, new_ball_shape = create_ball(18, (600, 300))

# Create balls and arrange them in a triangular formation
balls = []
lineup = 5
for ball in range(5):
    for row in range(lineup):
        position = (250 + (ball * Lily), 267 + (row * Lily) + (ball * Lily / 2))
        ball_body, ball_shape = create_ball(Lily / 2, position)
        balls.append(ball_body)
    lineup -= 1

# Add a ball in the center
position = (888, HEIGHT / 2)
ball_body, ball_shape = create_ball(Lily / 2, position)
balls.append(ball_body)

# Define pockets positions and hole width
pockets = [
    # Top pockets:
    (132, 104, hole_width),     #  left edge
    (593, 94, hole_width),    # mid edge
    (1053, 106, hole_width),   # right edge
    # Down pockets:
    (125, 569, hole_width),     #  left edge
    (589, 580, hole_width),    # mid edge
    (1057, 570, hole_width)    # right edge
]

# Define table borders
borders = [
    # Horizontal borders:
    [(571, 107), (574, 88), (142, 86), (166, 107)],  # Top left edge
    [(614, 88), (617, 107), (1048, 86), (1026, 106)],  # Top right edge
    [(137, 581), (160, 562), (572, 582), (568, 563)],  # Bottom left edge
    [(611, 562), (611, 581), (1024, 567), (1047, 586)],  # Bottom right edge
    # Vertical borders:
    [(110, 556), (131, 537), (114, 109), (136, 134)],  # Left edge
    [(1075, 561), (1054, 541), (1075, 112), (1054, 133)]  # Right edge
]

def create_border(points):
    """
    Function to create a table border.
    """
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Poly(body, points)
    shape.elasticity = 0.8
    space.add(body, shape)

# Create the table borders
for border in borders:
    create_border(border)

class Cue:
    """
    Class representing the cue stick.
    """
    def __init__(self, pos):
        self.original_image = cane
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self, angle):
        """
        Update the angle of the cue.
        """
        self.angle = angle

    def draw(self, surface):
        """
        Draw the cue on the given surface.
        """
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image, (
            self.rect.centerx - self.image.get_width() / 2,
            self.rect.centery - self.image.get_height() / 2
        ))

# Initialize the cue object with the position of the last ball
cue = Cue(balls[-1].position)

# Set up drawing options for Pymunk with Pygame
draw_options = pymunk.pygame_util.DrawOptions(window)


def stop_collision_sound():
    pygame.mixer.Sound.stop(collision_sound)
def post_solve(arbiter, space, data):
    if arbiter.total_impulse.length > 100:
        pygame.mixer.Sound.play(collision_sound)
        threading.Timer(0.5, stop_collision_sound).start()  # Stop sound after 0.1 seconds
# Set the post-solve collision handler
space.add_collision_handler(0, 0).post_solve = post_solve


# Define game states
WELCOME = 0
PLAYING = 1
game_state = WELCOME

# Main game loop
running = True
while running:
    welcome_background = pygame.image.load('welcome_background/1 (1).jpg').convert()

    if game_state == WELCOME:
        # Display background image
        window.blit(welcome_background, (0, 0))
        # Check for space key press to start the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = PLAYING

        # Check for space key press to start the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = PLAYING

    elif game_state == PLAYING:
        # Draw the table image and cue
        window.blit(table, (0, 0))
        cue.draw(window)

        # Draw all balls
        for i, ball in enumerate(balls):
            window.blit(ball_picture[i], (ball.position[0] - new_ball_shape.radius, ball.position[1] - new_ball_shape.radius))

        # Display message if any
        if display_message:
            message_text = font.render(display_message, True, (255, 255, 255))
            window.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, 20))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and shoot:
                power = True
            if event.type == pygame.MOUSEBUTTONUP and shoot:
                power = False
                x_push = math.cos(math.radians(cue.angle))
                y_push = math.sin(math.radians(cue.angle))
                balls[-1].apply_impulse_at_local_point((force * -x_push, force * y_push), (0, 0))
                force = 0
            if event.type == pygame.QUIT:
                running = False

        # Increase force while the mouse button is held down
        if power:
            force += 150

        # Check if any ball is still moving
        shoot = all(int(ball.velocity[0]) == 0 and int(ball.velocity[1]) == 0 for ball in balls)
        if shoot:
            mouse_pos = pygame.mouse.get_pos()
            cue.rect.center = balls[-1].position
            X_movement = balls[-1].position[0] - mouse_pos[0]
            Y_movement = -(balls[-1].position[1] - mouse_pos[1])
            cue_angle = math.degrees(math.atan2(Y_movement, X_movement))
            cue.update(cue_angle)
            cue.draw(window)

        # Check if any ball falls into a pocket
        for i, ball in enumerate(balls):
            for pocket in pockets:
                ball_x_dist = abs(ball.position[0] - pocket[0])
                ball_y_dist = abs(ball.position[1] - pocket[1])
                ball_dist = math.sqrt(ball_x_dist ** 2 + ball_y_dist ** 2)
                if ball_dist <= pocket[2] / 2:
                    if i == len(balls) - 1:
                        cue_ball_well = True
                        ball.position = (-100, -100)
                        ball.position = (0.0, 0.0)
                    else:
                        space.remove(ball)
                        balls.remove(ball)
                        well.append(ball_picture[i])
                        ball_picture.pop(i)

                        # Update the message based on the number of balls pocketed
                        message_counter += 1
                        if message_counter % 4 == 1:
                            display_message = 'Good!'
                        elif message_counter % 4 == 2:
                            display_message = 'Excellent!'
                        elif message_counter % 4 == 3:
                            display_message = "You're a pro!"
                        elif message_counter % 4 == 0:
                            display_message = 'Amazing!'

        # Update the physics simulation with a fixed time step
        space.step(1 / FPS)

        # Optionally draw Pymunk debug information
        # space.debug_draw(draw_options)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Clean up and exit
pygame.quit()
sys.exit()


