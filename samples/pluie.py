import pygame
import random

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH = 800
HEIGHT = 600

# Couleurs
BLACK = (0, 0, 0)

# Paramètres des particules
num_particles = 300
particle_size = 2
particle_speed = 5

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pluie de particules multicolores")

# Fonction pour générer une particule de pluie avec une couleur aléatoire
def create_particle():
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return {"x": x, "y": y, "color": color}

# Liste pour stocker les particules
particles = [create_particle() for _ in range(num_particles)]

# Boucle principale
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)

    # Gérer les événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Mettre à jour et afficher les particules
    for particle in particles:
        pygame.draw.circle(screen, particle['color'], (particle['x'], particle['y']), particle_size)
        particle['y'] += particle_speed

        # Réinitialiser la particule si elle sort de l'écran
        if particle['y'] > HEIGHT:
            particle['y'] = 0
            particle['x'] = random.randint(0, WIDTH)
            particle['color'] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    pygame.display.flip()
    clock.tick(60)

# Quitter Pygame
pygame.quit()
