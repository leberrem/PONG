import pygame
import random
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH = 800
HEIGHT = 600

# Couleurs
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)

# Paramètres des particules
num_particles = 100
particle_size = 2
particle_speed = 3
particle_colors = [YELLOW, ORANGE, RED]

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Effet visuel d'impact avec Pygame")

# Fonction pour générer une particule d'impact
def create_particle(x, y):
    color = random.choice(particle_colors)
    angle = random.uniform(0, 2 * 3.14159)
    speed = random.uniform(0.5, 1.0) * particle_speed
    return {"x": x, "y": y, "color": color, "angle": angle, "speed": speed}

# Liste pour stocker les particules
particles = []

# Boucle principale
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)

    # Gérer les événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Gérer l'impact (ajouter des particules)
    if pygame.mouse.get_pressed()[0]:
        mouse_pos = pygame.mouse.get_pos()
        for _ in range(num_particles):
            particles.append(create_particle(mouse_pos[0], mouse_pos[1]))

    # Mettre à jour et afficher les particules
    for particle in particles:
        particle['x'] += particle['speed'] * math.cos(particle['angle'])
        particle['y'] += particle['speed'] * math.sin(particle['angle'])

        # Dessiner la particule
        pygame.draw.circle(screen, particle['color'], (int(particle['x']), int(particle['y'])), particle_size)

        # Supprimer les particules qui sortent de l'écran
        if particle['x'] < 0 or particle['x'] > WIDTH or particle['y'] < 0 or particle['y'] > HEIGHT:
            particles.remove(particle)

    pygame.display.flip()
    clock.tick(60)

# Quitter Pygame
pygame.quit()
