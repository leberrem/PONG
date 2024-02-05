import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Taille de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Affichage d'une image png")

# Charger l'image
image = pygame.image.load("atari.png")  # Remplacez "image.jpg" par le chemin de votre image JPG

# Boucle principale
def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))  # Remplir l'écran en noir (facultatif)

        # Afficher l'image au centre de l'écran
        screen.blit(image, ((WIDTH - image.get_width()) // 2, (HEIGHT - image.get_height()) // 2))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
