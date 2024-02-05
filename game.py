#!/usr/bin/python3
import pygame
import random
import math
import pygame.gfxdraw
import io
import locale
import sys

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
pygame.display.set_caption("Pong")

if locale.getlocale()[0] == "fr_FR":
    LOOSE_TXT="PERDU"
    WIN_TXT="GAGNE"
else:
    LOOSE_TXT="LOOSE"
    WIN_TXT="WIN"

DIRECTION_UP, DIRECTION_DOWN, DIRECTION_RIGHT, DIRECTION_LEFT = 0, 1, 2, 3

SPACE_WIDTH = 5 # Taille des espaces
LINE_WIDTH = 5 # Epaisseurs des lignes
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100 # Taille des raquettes
PADDLE_SPEED = 10 # Vitesse de déplacement des raquettes
BALL_SIZE = 20 # Taille de la balle
BALL_SPEED_X = 5 # Vitesse de déplacemant horizontale de la balle
BALL_SPEED_Y = 5 # Vitesse de déplacemant verticale de la balle
BALL_INERTIA = 9 # Inertie de la balle
BALL_ACCELERATION = 0.2 # Accélération de la balle à chaque rebond
BALL_REPLACE_DURATION = 30 # Vitesse d'apparition et disparition de la balle
BALL_INIT_SPEED = 8  # Vitesse de la balle
HALO_FRAME_COUNT = 2 # Nombre de flash du halo
HALO_FRAME_SPEED = 5 # Vitesse du halo
HALO_FRAME_WIDTH = 15 # epaisseur maximale du halo
WIN_SCORE = 1 # Score à obtenir pour gagner
FONT_SIZE = 80 # Taille de la police de caractères
DASH_LENGTH = 10 # Définition du motif de pointillé
FIREWORK_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (255, 192, 203), (255, 0, 255)] # Jeu de couleur du feu d'artifice

# current player
current_player = 0
# Scores
left_score = 0
right_score = 0
font = pygame.font.Font("SevenSegment.ttf", FONT_SIZE)

# Effets visuels
no_effect = False
dust_effects = []
firework_effects = []
Halo_frame_effects = []
ball_replace_timer = 0
last_ball_x_position = 0
last_ball_y_position = 0

# ####################################################
# Classes
# ####################################################

class Dust_particle:
    def __init__(self, x, y, color, direction):
        self.x, self.y = x, y
        self.color = color
        self.direction = direction
        if direction == DIRECTION_UP:
            self.vx, self.vy = random.randint(-2, 2), random.randint(-10, 0)*.1
        if direction == DIRECTION_DOWN:
            self.vx, self.vy = random.randint(-2, 2), -random.randint(-10, 0)*.1
        if direction == DIRECTION_LEFT:
            self.vx, self.vy = random.randint(-10, 0)*.1, random.randint(-2, 2)
        if direction == DIRECTION_RIGHT:
            self.vx, self.vy = -random.randint(-10, 0)*.1, random.randint(-2, 2)
        self.radius = 5

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))

    def move(self):
        self.x += self.vx
        self.y += self.vy
        if random.randint(0, 100) < 40:
            self.radius -= 1

class Dust:
    def __init__(self, x, y, color, direction):
        self.x = x
        self.y = y
        self.color = color
        self.direction = direction
        self.particles = []
        for i in range(100):
            self.particles.append(Dust_particle(self.x, self.y, self.color, self.direction))

    def update(self):
        for i in self.particles:
            if i.radius > 0:
                i.move()
                #self.particles = [particle for particle in self.particles if particle.radius > 0]
            else:
                self.particles.remove(i)
                del i

    def draw(self):
        for i in self.particles:
            i.draw()

class Firework_particle:
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

class Firework:
    def __init__(self, x, y, color, direction):
        self.x = x
        self.y = y
        self.color = color
        self.exploded = False
        self.particles = []
        self.direction = direction

    def explode(self):
        for _ in range(50):
            particle = Firework_particle(self.x, self.y, self.color)
            self.particles.append(particle)

    def move(self):
        if not self.exploded:
            if self.direction == DIRECTION_RIGHT:
                self.x += 5
                if self.x >= random.randint(int(WIDTH * 0.25), WIDTH // 2 - 50):
                    self.exploded = True
                    self.explode()
            if self.direction == DIRECTION_LEFT:
                self.x -= 5
                if self.x <= random.randint(WIDTH // 2 + 50, int(WIDTH * 0.75)):
                    self.exploded = True
                    self.explode()
        else:
            for particle in self.particles:
                particle.move()
                if particle.life <= 0:
                    self.particles.remove(particle)
                    del particle

    def draw(self):
        if not self.exploded:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)
        else:
            for particle in self.particles:
                particle.draw()

class Halo_frame:
    def __init__(self, width, count, speed):
        self.count = count
        self.width = width
        self.speed = speed
        self.line_width = 1
        self.direction = 1

    def move(self):
        if self.count > 0 :
            if self.line_width <= 0:
                self.direction = 1
                self.count -= 1
            if self.line_width >= self.width:
                self.direction = -1
            self.line_width += self.speed * self.direction

    def draw(self):
        pygame.draw.line(screen, WHITE, (0,0), (WIDTH,0), self.line_width)
        pygame.draw.line(screen, WHITE, (WIDTH,0), (WIDTH,HEIGHT), self.line_width)
        pygame.draw.line(screen, WHITE, (WIDTH,HEIGHT), (0,HEIGHT), self.line_width)
        pygame.draw.line(screen, WHITE, (0,HEIGHT), (0,0), self.line_width)

# ####################################################
# Fonctions
# ####################################################

# Fonction pour vérifier si on est sur raspberry pi
def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower():
                return True
    except Exception: pass
    return False

# Fonction pour dessiner les raquettes
def draw_paddles(left_paddle_y, right_paddle_y):
    pygame.draw.rect(screen, WHITE, (0 + LINE_WIDTH, left_paddle_y - PADDLE_HEIGHT // 2 , PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(screen, WHITE, (WIDTH - PADDLE_WIDTH - LINE_WIDTH, right_paddle_y - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT))

# Fonction pour dessiner la balle
def draw_ball(ball_x, ball_y, color):
    pygame.draw.rect(screen, color, (int(ball_x-BALL_SIZE//2), int(ball_y-BALL_SIZE//2), int(BALL_SIZE), int(BALL_SIZE)))

# Fonction pour afficher le score
def draw_score():
    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (WIDTH // 2 - 60, 20))
    screen.blit(right_text, (WIDTH // 2 + 20, 20))

# Fonction pour afficher une ligne en pointillés
def draw_dashed_line(surface, color, start_pos, end_pos, width=1, dash_length=10):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx, dy = x2 - x1, y2 - y1
    distance = max(abs(dx), abs(dy))
    dx = dx / distance
    dy = dy / distance
    for i in range(0, int(distance/dash_length), 2):
        start = round(x1 + i * dx * dash_length), round(y1 + i * dy * dash_length)
        end = round(x1 + (i + 1) * dx * dash_length), round(y1 + (i + 1) * dy * dash_length)
        pygame.draw.line(surface, color, start, end, width)

# Fonction pour afficher une ligne en pointillés
def draw_frame(surface, color, width=1):
    pygame.draw.line(surface, color, (0,0), (WIDTH,0), width)
    pygame.draw.line(surface, color, (WIDTH,0), (WIDTH,HEIGHT), width)
    pygame.draw.line(surface, color, (WIDTH,HEIGHT), (0,HEIGHT), width)
    pygame.draw.line(surface, color, (0,HEIGHT), (0,0), width)

# ####################################################
# Fonction principale
# ####################################################

def main():
    global left_score, right_score, screen, no_effect

    current_player = random.randint(1, 2)
    clock = pygame.time.Clock()
    left_paddle_y = HEIGHT // 2
    right_paddle_y = HEIGHT // 2
    ball_speed = BALL_INIT_SPEED
    ball_speed_x = 0
    ball_speed_y = 0
    game_started = False
    game_paused = False
    ball_replace_timer = 0

    if len(sys.argv) > 1:
        if sys.argv[1] == "--no_effect":
            no_effect = True

    if is_raspberrypi():
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        icon_32x32 = pygame.image.load("logo.png").convert_alpha()
        pygame.display.set_icon(icon_32x32)

    # Initialisation de la position de la balle
    if ( current_player == 1 ):
        ball_x = PADDLE_WIDTH + SPACE_WIDTH + BALL_SIZE // 2 + LINE_WIDTH
        ball_y = left_paddle_y
    elif ( current_player == 2 ):
        ball_x = WIDTH - PADDLE_WIDTH - SPACE_WIDTH - BALL_SIZE // 2 - LINE_WIDTH
        ball_y = right_paddle_y

    running = True
    while running:

        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_LCTRL and not game_started and not game_paused:
                    # re-initialisation des scores
                    if right_score >= WIN_SCORE:
                        right_score = 0
                        left_score = 0
                    # Lancement de la balle à droite
                    if ( current_player == 1 ):
                        if not no_effect: dust_effects.append(Dust(ball_x-BALL_SIZE // 2, ball_y, WHITE, DIRECTION_RIGHT))
                        # Calcul de l'angle de rebond basé sur la position relative de la balle sur la raquette
                        relative_intersect_y = left_paddle_y - ball_y
                        normalized_intersect_y = relative_intersect_y / (PADDLE_HEIGHT // 2 + BALL_SIZE // 2)
                        bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degrés)
                        ball_speed_x = ball_speed * math.cos(bounce_angle)
                        ball_speed_y = ball_speed * -math.sin(bounce_angle)
                        game_started = True
                    # Lancement de la balle à droite
                    if not no_effect:
                        if ( current_player == 2  and left_score >= WIN_SCORE ):
                            firework_color = random.choice(FIREWORK_COLORS)
                            firework_effects.append(Firework(PADDLE_WIDTH + SPACE_WIDTH, left_paddle_y, firework_color, DIRECTION_RIGHT))
                            dust_effects.append(Dust(PADDLE_WIDTH + SPACE_WIDTH, left_paddle_y, firework_color, DIRECTION_RIGHT))
                if event.key == pygame.K_RCTRL and not game_started and not game_paused:
                    # re-initialisation des scores
                    if left_score >= WIN_SCORE:
                        right_score = 0
                        left_score = 0
                    # Lancement de la balle à gauche
                    if ( current_player == 2 ):
                        if not no_effect: dust_effects.append(Dust(ball_x+BALL_SIZE // 2, ball_y, WHITE, DIRECTION_LEFT))
                        # Calcul de l'angle de rebond basé sur la position relative de la balle sur la raquette
                        relative_intersect_y = right_paddle_y - ball_y
                        normalized_intersect_y = relative_intersect_y / (PADDLE_HEIGHT // 2 + BALL_SIZE // 2)
                        bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degrés)
                        ball_speed_x = -ball_speed * math.cos(bounce_angle)
                        ball_speed_y = ball_speed * -math.sin(bounce_angle)
                        game_started = True
                    if ( current_player == 1 and right_score >= WIN_SCORE):
                        if not no_effect:
                            firework_color = random.choice(FIREWORK_COLORS)
                            firework_effects.append(Firework(WIDTH - PADDLE_WIDTH - SPACE_WIDTH, right_paddle_y, firework_color, DIRECTION_LEFT))
                            dust_effects.append(Dust(WIDTH - PADDLE_WIDTH - SPACE_WIDTH, right_paddle_y, firework_color, DIRECTION_LEFT))
        keys = pygame.key.get_pressed()
        if game_paused == False:
            if keys[pygame.K_w] or keys[pygame.K_z]:
                if left_paddle_y >= LINE_WIDTH + SPACE_WIDTH + PADDLE_HEIGHT // 2:
                    if abs(left_paddle_y - (LINE_WIDTH + SPACE_WIDTH + PADDLE_HEIGHT // 2)) < PADDLE_SPEED:
                        left_paddle_y = LINE_WIDTH + PADDLE_HEIGHT // 2
                    else:
                        left_paddle_y -= PADDLE_SPEED
            if keys[pygame.K_s]:
                if left_paddle_y <= HEIGHT - LINE_WIDTH - SPACE_WIDTH - PADDLE_HEIGHT // 2:
                    if abs(left_paddle_y - (HEIGHT - LINE_WIDTH - SPACE_WIDTH - PADDLE_HEIGHT // 2)) < PADDLE_SPEED:
                        left_paddle_y = HEIGHT - LINE_WIDTH - PADDLE_HEIGHT // 2
                    else:
                        left_paddle_y += PADDLE_SPEED
            if keys[pygame.K_UP]:
                if right_paddle_y >= LINE_WIDTH + SPACE_WIDTH + PADDLE_HEIGHT // 2:
                    if abs(right_paddle_y - (LINE_WIDTH + SPACE_WIDTH + PADDLE_HEIGHT // 2)) < PADDLE_SPEED:
                        right_paddle_y = LINE_WIDTH + PADDLE_HEIGHT // 2
                    else:
                        right_paddle_y -= PADDLE_SPEED
            if keys[pygame.K_DOWN]:
                if right_paddle_y <= HEIGHT - LINE_WIDTH - SPACE_WIDTH - PADDLE_HEIGHT // 2:
                    if abs(right_paddle_y - (HEIGHT - LINE_WIDTH - SPACE_WIDTH - PADDLE_HEIGHT // 2)) < PADDLE_SPEED:
                        right_paddle_y = HEIGHT - LINE_WIDTH - PADDLE_HEIGHT // 2
                    else:
                        right_paddle_y += PADDLE_SPEED

        if game_started == True:

            ball_x += ball_speed_x
            ball_y += ball_speed_y

            # rebond de la balle sur le haut
            if ball_y <= BALL_SIZE//2:
                ball_speed_y = -ball_speed_y
                if not no_effect: dust_effects.append(Dust(ball_x, ball_y - BALL_SIZE//2, WHITE, DIRECTION_DOWN))

            # rebond de la balle sur la bas
            if ball_y >= HEIGHT - BALL_SIZE//2:
                ball_speed_y = -ball_speed_y
                if not no_effect: dust_effects.append(Dust(ball_x, ball_y + BALL_SIZE//2, WHITE, DIRECTION_UP))

            # rebond de la balle sur la raquette gauche
            if ball_x <= LINE_WIDTH + SPACE_WIDTH + PADDLE_WIDTH + BALL_SIZE // 2 and left_paddle_y - PADDLE_HEIGHT // 2 - BALL_SIZE // 2 < ball_y < left_paddle_y + PADDLE_HEIGHT // 2 + BALL_SIZE // 2 :
                ball_speed += BALL_ACCELERATION * (1 if ball_speed > 0 else -1)  # Augmentation de la vitesse
                ball_speed_x = -ball_speed_x
                if ball_x < LINE_WIDTH + SPACE_WIDTH + PADDLE_WIDTH + BALL_SIZE // 2:
                    ball_x = LINE_WIDTH + SPACE_WIDTH + PADDLE_WIDTH + BALL_SIZE // 2
                if not no_effect: dust_effects.append(Dust(ball_x - BALL_SIZE // 2, ball_y, WHITE, DIRECTION_RIGHT))
                # Calcul de l'angle de rebond basé sur la position relative de la balle sur la raquette
                relative_intersect_y = left_paddle_y - ball_y
                normalized_intersect_y = relative_intersect_y / (PADDLE_HEIGHT / 2 + BALL_SIZE // 2)
                bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degrés)
                ball_speed_x = ball_speed * math.cos(bounce_angle)
                ball_speed_y = ball_speed * -math.sin(bounce_angle)

            # rebond de la balle sur la raquette droite
            if ball_x >= WIDTH - LINE_WIDTH - SPACE_WIDTH - PADDLE_WIDTH - BALL_SIZE // 2 and right_paddle_y  - PADDLE_HEIGHT // 2 - BALL_SIZE // 2 < ball_y < right_paddle_y + PADDLE_HEIGHT // 2 + BALL_SIZE // 2:
                ball_speed += BALL_ACCELERATION * (1 if ball_speed > 0 else -1)  # Augmentation de la vitesse
                ball_speed_x = -ball_speed_x
                if ball_x > WIDTH - LINE_WIDTH - SPACE_WIDTH - PADDLE_WIDTH - BALL_SIZE // 2:
                    ball_x = WIDTH - LINE_WIDTH - SPACE_WIDTH - PADDLE_WIDTH - BALL_SIZE // 2
                if not no_effect: dust_effects.append(Dust(ball_x + BALL_SIZE // 2, ball_y, WHITE, DIRECTION_LEFT))
                # Calcul de l'angle de rebond basé sur la position relative de la balle sur la raquette
                relative_intersect_y = right_paddle_y - ball_y
                normalized_intersect_y = relative_intersect_y / (PADDLE_HEIGHT / 2 + BALL_SIZE // 2)
                bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degrés)
                ball_speed_x = -ball_speed * math.cos(bounce_angle)
                ball_speed_y = ball_speed * -math.sin(bounce_angle)

            # Sortie de la balle à gauche
            if ball_x <= LINE_WIDTH + SPACE_WIDTH + BALL_SIZE // 2:
                right_score += 1
                last_ball_x_position = ball_x
                last_ball_y_position = ball_y
                ball_speed_x = 0
                ball_speed_y = 0
                game_started = False
                game_paused = True
                ball_replace_timer = BALL_REPLACE_DURATION
                current_player = 1
                if not no_effect: Halo_frame_effects.append(Halo_frame(HALO_FRAME_WIDTH, HALO_FRAME_COUNT, HALO_FRAME_SPEED))
                if right_score >= WIN_SCORE:
                    ball_speed = BALL_INIT_SPEED
                    game_started = False

            # Sortie de la balle à droite
            if ball_x >= WIDTH - LINE_WIDTH - SPACE_WIDTH - BALL_SIZE // 2:
                left_score += 1
                last_ball_x_position = ball_x
                last_ball_y_position = ball_y
                ball_speed_x = 0
                ball_speed_y = 0
                game_started = False
                game_paused = True
                ball_replace_timer = BALL_REPLACE_DURATION
                current_player = 2
                if not no_effect: Halo_frame_effects.append(Halo_frame(HALO_FRAME_WIDTH, HALO_FRAME_COUNT, HALO_FRAME_SPEED))
                if left_score >= WIN_SCORE:
                    ball_speed = BALL_INIT_SPEED
                    game_started = False

        else:

            if game_paused == False:

                # Suivi de la balle sur la raquette
                ball_speed_x = 0
                ball_speed_y = 0
                if ( current_player == 1 ):
                    ball_x = PADDLE_WIDTH + SPACE_WIDTH + BALL_SIZE // 2 + LINE_WIDTH
                    if abs(ball_y - left_paddle_y) < BALL_INERTIA:
                        ball_y = left_paddle_y
                    if ball_y < left_paddle_y:
                        ball_y += BALL_INERTIA
                    if ball_y > left_paddle_y:
                        ball_y -= BALL_INERTIA
                elif ( current_player == 2 ):
                    ball_x = WIDTH - PADDLE_WIDTH - SPACE_WIDTH - BALL_SIZE // 2 - LINE_WIDTH
                    if abs(ball_y - right_paddle_y) < BALL_INERTIA:
                        ball_y = right_paddle_y
                    if ball_y < right_paddle_y:
                        ball_y += BALL_INERTIA
                    if ball_y > right_paddle_y:
                        ball_y -= BALL_INERTIA

            # Victoire à gauche
            if left_score >= WIN_SCORE:
                looser_text = font.render(LOOSE_TXT, True, WHITE)
                looser_text = pygame.transform.rotate(looser_text, 90)
                screen.blit(looser_text, (int(WIDTH * 0.75 - FONT_SIZE // 2), int(HEIGHT // 2 - (len(LOOSE_TXT) * FONT_SIZE / 4)) ))
                winner_text = font.render(WIN_TXT, True, WHITE)
                winner_text = pygame.transform.rotate(winner_text, 270)
                screen.blit(winner_text, (int(WIDTH * 0.25 - FONT_SIZE // 2), int(HEIGHT // 2 - (len(WIN_TXT) * FONT_SIZE / 4)) ))

            # Victoire à droite
            if right_score >= WIN_SCORE:
                winner_text = font.render(WIN_TXT, True, WHITE)
                winner_text = pygame.transform.rotate(winner_text, 90)
                screen.blit(winner_text, (int(WIDTH * 0.75 - FONT_SIZE // 2), int(HEIGHT // 2 - (len(WIN_TXT) * FONT_SIZE / 4)) ))
                looser_text = font.render(LOOSE_TXT, True, WHITE)
                looser_text = pygame.transform.rotate(looser_text, 270)
                screen.blit(looser_text, (int(WIDTH * 0.25 - FONT_SIZE // 2), int(HEIGHT // 2 - (len(LOOSE_TXT) * FONT_SIZE / 4)) ))

        # Replacement de la balle
        if game_paused == True and ball_replace_timer > 0:
            ball_replace_timer -= 1
            percent = ball_replace_timer / BALL_REPLACE_DURATION
            if current_player == 1:
                ball_x = (PADDLE_WIDTH + SPACE_WIDTH + BALL_SIZE // 2 + LINE_WIDTH) - (((PADDLE_WIDTH + SPACE_WIDTH + BALL_SIZE // 2) - last_ball_x_position) * percent)
                ball_y = left_paddle_y - ((left_paddle_y - last_ball_y_position) * percent)
            if current_player == 2:
                ball_x = (WIDTH - PADDLE_WIDTH - SPACE_WIDTH - BALL_SIZE // 2 - LINE_WIDTH) - (((WIDTH - PADDLE_WIDTH - SPACE_WIDTH - BALL_SIZE // 2) - last_ball_x_position) * percent)
                ball_y = right_paddle_y - ((right_paddle_y - last_ball_y_position) * percent)

        # Reprise du jeu
        if game_paused == True and ball_replace_timer <= 0:
            game_paused = False

        # Limiter la vitesse de la balle
        ball_speed_x = max(min(ball_speed_x, 20), -20)
        ball_speed_y = max(min(ball_speed_y, 20), -20)

        # Mise à jour et dessin des effets de particules
        for particle in dust_effects:
            if len(particle.particles) > 0:
                particle.update()
                particle.draw()
            else:
                dust_effects.remove(particle)
                del particle

        for firework in firework_effects:
            if len(firework.particles) > 0 or firework.exploded == False:
                firework.move()
                firework.draw()
            else:
                firework_effects.remove(firework)
                del firework

        for halo in Halo_frame_effects:
            if halo.count > 0:
                halo.move()
                halo.draw()
            else:
                Halo_frame_effects.remove(halo)
                del halo

        draw_frame(screen, WHITE, LINE_WIDTH)
        draw_dashed_line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), LINE_WIDTH, DASH_LENGTH)
        draw_paddles(left_paddle_y, right_paddle_y)
        draw_ball(ball_x, ball_y, WHITE)
        draw_score()

        pygame.display.flip()

        # Limiter la vitesse de la boucle à 60 FPS
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
