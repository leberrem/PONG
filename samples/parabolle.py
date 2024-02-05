import pygame
import sys

# Initialize pygame
pygame.init()

# Set the dimensions of the screen
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ball in Parabolic Path")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Ball properties
ball_radius = 10
ball_color = RED
ball_speed = 5
gravity = 0.1

# Initial position and velocity of the ball
initial_x = width // 2
initial_y = height - ball_radius
initial_velocity = -10  # Initial upward velocity

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(WHITE)

    # Update the position of the ball
    initial_y += initial_velocity
    initial_velocity += gravity

    # Draw the ball
    pygame.draw.circle(screen, ball_color, (initial_x, int(initial_y)), ball_radius)

    # Update the display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()
