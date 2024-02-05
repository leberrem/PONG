import pygame
import random
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH = 800
HEIGHT = 600

# Couleurs
BLACK = (0, 0, 0)

# Paramètres des particules
num_particles = 100
particle_size = 2
particle_speed = 5
particle_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (255, 192, 203), (255, 255, 255)]

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Feu d'artifice en particules")

# Fonction pour générer une particule de feu d'artifice
def create_particle():
    x = WIDTH // 2
    y = HEIGHT
    color = random.choice(particle_colors)
    angle = random.uniform(0, math.pi * 2)
    speed = random.uniform(0.5, 1.0) * particle_speed
    return {"x": x, "y": y, "color": color, "angle": angle, "speed": speed}

# Liste pour stocker les particules
particles = []

# Boucle principale
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)

    # Gérer les événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Générer de nouvelles particules lorsque le bouton de la souris est enfoncé
    if pygame.mouse.get_pressed()[0]:
        for _ in range(num_particles):
            particles.append(create_particle())

    # Mettre à jour et afficher les particules
    for particle in particles:
        particle['x'] += math.cos(particle['angle']) * particle['speed']
        particle['y'] -= math.sin(particle['angle']) * particle['speed']
        pygame.draw.circle(screen, particle['color'], (int(particle['x']), int(particle['y'])), particle_size)

        # Supprimer les particules qui sont hors de l'écran
        if particle['x'] < 0 or particle['x'] > WIDTH or particle['y'] < 0 or particle['y'] > HEIGHT:
            particles.remove(particle)

    pygame.display.flip()
    clock.tick(60)

# Quitter Pygame
pygame.quit()
