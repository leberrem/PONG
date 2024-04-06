import pygame
import math
import random

# Initialisation de Pygame
pygame.init()

# Définition des couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Paramètres de la fenêtre
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scorched Earth")

# Définition des constantes
GRAVITY = 0.25

# Génération du terrain aléatoire avec lissage
def generate_terrain():
    terrain = [random.randint(300, 500) for _ in range(WIDTH)]
    smooth_terrain = [sum(terrain[max(0, i - 2):min(WIDTH, i + 3)]) / min(5, i + 3, WIDTH - i + 2) for i in range(WIDTH)]
    return smooth_terrain

# Classe représentant les projectiles
class Projectile:
    def __init__(self, x, y, angle, power, color):
        self.x = x
        self.y = y
        self.angle = angle
        self.power = power
        self.color = color
        self.vel_x = math.cos(angle) * power
        self.vel_y = -math.sin(angle) * power
        self.time = 0

    def draw(self):
        pygame.draw.circle(WIN, self.color, (round(self.x), round(self.y)), 5)

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY
        self.time += 1

# Fonction principale du jeu
def main():
    clock = pygame.time.Clock()
    run = True
    terrain = generate_terrain()
    projectiles = []

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                angle = math.atan2(HEIGHT - mouse_y, mouse_x)
                power = math.hypot(mouse_x, HEIGHT - mouse_y) / 10
                projectiles.append(Projectile(0, HEIGHT, angle, power, GREEN))

        for projectile in projectiles:
            if projectile.x < 0 or projectile.y > terrain[round(projectile.x)]:
                projectiles.remove(projectile)
            projectile.move()

        WIN.fill(BLACK)
        pygame.draw.polygon(WIN, WHITE, [(i, terrain[i]) for i in range(WIDTH)])
        for projectile in projectiles:
            projectile.draw()

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()