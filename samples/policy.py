import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH = 800
HEIGHT = 600

# Couleurs
WHITE = (255, 255, 255)

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Texte avec police à segments")

# Charger la police à segments
font = pygame.font.Font("SevenSegment.ttf", 36)

# Texte à afficher
text = "Hello, World!"

# Rendu du texte avec la police à segments
rendered_text = font.render(text, True, WHITE)

# Position du texte
text_rect = rendered_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Boucle principale
running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Affichage du texte
    screen.blit(rendered_text, text_rect)

    pygame.display.flip()

# Quitter Pygame
pygame.quit()
