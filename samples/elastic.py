import pygame
import math

# Initialisation de Pygame
pygame.init()

# Définition de quelques couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Définition des dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Effet d'élastique")

# Variables de position et de longueur de l'élastique
elastic_x = WIDTH // 2
elastic_y = HEIGHT // 2
elastic_length = 200

# Variables de mouvement de l'élastique
angle = 0
angular_speed = 0.05

# Boucle principale du jeu
running = True
while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Effacement de l'écran
    screen.fill(WHITE)

    # Calcul des coordonnées de l'extrémité de l'élastique
    end_x = elastic_x + elastic_length * math.cos(angle)
    end_y = elastic_y + elastic_length * math.sin(angle)

    # Dessin de l'élastique
    pygame.draw.line(screen, BLACK, (elastic_x, elastic_y), (end_x, end_y), 2)
    pygame.draw.circle(screen, RED, (int(end_x), int(end_y)), 10)

    # Mise à jour de l'angle pour simuler le mouvement de l'élastique
    angle += angular_speed

    # Rafraîchissement de l'écran
    pygame.display.flip()

    # Limite de vitesse de la boucle
    pygame.time.Clock().tick(60)

# Fermeture de Pygame
pygame.quit()
