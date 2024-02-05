import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fireworks with Particle Effects")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Particle class
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 2 * math.pi)
        self.dx = self.speed * math.cos(self.angle)
        self.dy = self.speed * math.sin(self.angle)
        self.life = random.randint(10, 30)

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# Firework class
class Firework:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.exploded = False
        self.particles = []

    def explode(self):
        for _ in range(50):
            particle = Particle(self.x, self.y, self.color)
            self.particles.append(particle)

    def move(self):
        if not self.exploded:
            self.y -= 5
            if self.y <= random.randint(100, 350):
                self.exploded = True
                self.explode()
        else:
            for particle in self.particles:
                particle.move()
                if particle.life <= 0:
                    self.particles.remove(particle)

    def draw(self):
        if not self.exploded:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)
        else:
            for particle in self.particles:
                particle.draw()

# Main loop
fireworks = []

running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Create new fireworks
    if random.random() < 0.02:
        fireworks.append(Firework())

    # Update and draw fireworks
    for firework in fireworks:
        firework.move()
        firework.draw()
        if firework.y <= random.randint(50, 200) and not firework.exploded:
            fireworks.remove(firework)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
