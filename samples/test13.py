import pygame
import random
import math
import pygame.gfxdraw

# Initialisation de Pygame
pygame.init()

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_YELLOW = (255, 255, 204)

# Taille de l'écran
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Variables du jeu
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 5
BALL_SIZE = 20
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
BALL_ACCELERATION = 0.2  # Accélération de la balle à chaque rebond
BALL_SPEED = 5  # Vitesse de la balle
HALO_RADIUS_X = 80  # Rayon horizontal du halo
HALO_RADIUS_Y = 30  # Rayon vertical du halo
HALO_DURATION = 30  # Durée de l'effet de halo en frames

# Scores
left_score = 0
right_score = 0
font = pygame.font.Font(None, 36)

# Effets visuels
particle_effects = []
halo_timer = 0
last_bounce_position = None

# Classe de particule
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(2, 4)
        self.direction = random.uniform(0, 2 * 3.1415)
        self.speed = random.uniform(1, 4)

    def move(self):
        self.x += self.speed * 1.5 * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.radius -= 0.1

    def draw(self):
        pygame.draw.circle(SCREEN, self.color, (int(self.x), int(self.y)), int(self.radius))

# Fonction pour dessiner les raquettes
def draw_paddles(left_paddle_y, right_paddle_y):
    pygame.draw.rect(SCREEN, WHITE, (0, left_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(SCREEN, WHITE, (WIDTH - PADDLE_WIDTH, right_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))

# Fonction pour dessiner la balle
def draw_ball(ball_x, ball_y):
    pygame.draw.rect(SCREEN, WHITE, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))

# Fonction pour afficher le score
def draw_score():
    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    SCREEN.blit(left_text, (WIDTH // 2 - 50, 20))
    SCREEN.blit(right_text, (WIDTH // 2 + 30, 20))

# Fonction pour créer un effet de particules
def create_particle_effect(x, y, color, num_particles):
    for _ in range(num_particles):
        particle = Particle(x, y, color)
        particle_effects.append(particle)

# Fonction principale
def main():
    global left_score, right_score, halo_timer, last_bounce_position

    clock = pygame.time.Clock()
    left_paddle_y = (HEIGHT - PADDLE_HEIGHT) // 2
    right_paddle_y = (HEIGHT - PADDLE_HEIGHT) // 2
    ball_x = (WIDTH - BALL_SIZE) // 2
    ball_y = (HEIGHT - BALL_SIZE) // 2
    ball_speed_x = 0
    ball_speed_y = 0
    game_started = False

    running = True
    while running:
        SCREEN.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_started:
                    ball_speed_x = BALL_SPEED_X * random.choice((1, -1))
                    ball_speed_y = BALL_SPEED_Y * random.choice((1, -1))
                    game_started = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            left_paddle_y -= PADDLE_SPEED
        if keys[pygame.K_s]:
            left_paddle_y += PADDLE_SPEED
        if keys[pygame.K_UP]:
            right_paddle_y -= PADDLE_SPEED
        if keys[pygame.K_DOWN]:
            right_paddle_y += PADDLE_SPEED

        ball_x += ball_speed_x
        ball_y += ball_speed_y

        if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
            ball_speed_y = -ball_speed_y
            ball_speed_y += BALL_ACCELERATION * (1 if ball_speed_y > 0 else -1)  # Augmentation de la vitesse
            halo_timer = HALO_DURATION
            last_bounce_position = (ball_x + BALL_SIZE // 2, ball_y + BALL_SIZE // 2)

        if ball_x <= PADDLE_WIDTH and left_paddle_y < ball_y + BALL_SIZE < left_paddle_y + PADDLE_HEIGHT:
            ball_speed_x = -ball_speed_x
            create_particle_effect(ball_x + BALL_SIZE // 2, ball_y + BALL_SIZE // 2, RED, 30)
            # Calcul de l'angle de rebond basé sur la position relative de la balle sur la raquette
            relative_intersect_y = (left_paddle_y + PADDLE_HEIGHT / 2) - (ball_y + BALL_SIZE / 2)
            normalized_intersect_y = relative_intersect_y / (PADDLE_HEIGHT / 2)
            bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degrés)
            ball_speed_x = BALL_SPEED * math.cos(bounce_angle)
            ball_speed_y = BALL_SPEED * -math.sin(bounce_angle)

        if ball_x >= WIDTH - PADDLE_WIDTH - BALL_SIZE and right_paddle_y < ball_y + BALL_SIZE < right_paddle_y + PADDLE_HEIGHT:
            ball_speed_x = -ball_speed_x
            create_particle_effect(ball_x + BALL_SIZE // 2, ball_y + BALL_SIZE // 2, RED, 30)
            # Calcul de l'angle de rebond basé sur la position relative de la balle sur la raquette
            relative_intersect_y = (right_paddle_y + PADDLE_HEIGHT / 2) - (ball_y + BALL_SIZE / 2)
            normalized_intersect_y = relative_intersect_y / (PADDLE_HEIGHT / 2)
            bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degrés)
            ball_speed_x = -BALL_SPEED * math.cos(bounce_angle)
            ball_speed_y = BALL_SPEED * -math.sin(bounce_angle)

        if ball_x < 0:
            right_score += 1
            create_particle_effect(WIDTH // 2, HEIGHT // 2, GREEN, 50)
            ball_x = (WIDTH - BALL_SIZE) // 2
            ball_y = (HEIGHT - BALL_SIZE) // 2
            ball_speed_x = 0
            ball_speed_y = 0
            game_started = False

        if ball_x > WIDTH:
            left_score += 1
            create_particle_effect(WIDTH // 2, HEIGHT // 2, GREEN, 50)
            ball_x = (WIDTH - BALL_SIZE) // 2
            ball_y = (HEIGHT - BALL_SIZE) // 2
            ball_speed_x = 0
            ball_speed_y = 0
            game_started = False

        # Halo lumineux lors des rebonds sur les côtés
        if halo_timer > 0 and last_bounce_position:
            for i in range(1, HALO_RADIUS_X + 1):
                alpha = 100 - (i * (100 // HALO_RADIUS_X))
                pygame.gfxdraw.aacircle(SCREEN, int(last_bounce_position[0]), int(last_bounce_position[1]), i, (255, 255, 204, alpha))
            halo_timer -= 1

        # Limiter la vitesse de la balle
        ball_speed_x = max(min(ball_speed_x, 10), -10)
        ball_speed_y = max(min(ball_speed_y, 10), -10)

        # Dessiner le filet au milieu de l'écran
        pygame.draw.line(SCREEN, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 5)

        # Mise à jour et dessin des effets de particules
        for particle in particle_effects:
            particle.move()
            particle.draw()

        draw_paddles(left_paddle_y, right_paddle_y)
        draw_ball(ball_x, ball_y)
        draw_score()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
