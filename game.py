#!/usr/bin/python3

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import platform
import random
import math
import locale
import sys
import traceback
import logging
import colorama
from pygame.locals import *
from colorama import Fore, Back, Style

# Colorama
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

# Raspberry Pi load GPIO
_rpi_gpio_Loaded = True
try:
    import RPi.GPIO as GPIO
except:
    _rpi_gpio_Loaded = False

# Initialisation de Pygame
pygame.mixer.pre_init(44100,-16,2,2048)
pygame.init()

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

if locale.getlocale()[0] == "fr_FR":
    LOOSE_TXT="PERDU"
    WIN_TXT="GAGNE"
else:
    LOOSE_TXT="LOOSE"
    WIN_TXT="WIN"

DIRECTION_UP, DIRECTION_DOWN, DIRECTION_RIGHT, DIRECTION_LEFT = 0, 1, 2, 3

SPACE_WIDTH = 5 # Taille des espaces
LINE_WIDTH = 5 # Epaisseurs des lignes
BALL_ACCELERATION = 0.2 # Acceleration de la balle a chaque rebond
BALL_REPLACE_DURATION = 30 # Temps de replacement de la balle sur la raquette
HALO_FRAME_COUNT = 2 # Nombre de flash du halo
HALO_FRAME_SPEED = 5 # Vitesse du halo
HALO_FRAME_WIDTH = 15 # epaisseur maximale du halo
WIN_SCORE = 8 # Score a obtenir pour gagner
FIREWORK_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (255, 192, 203), (255, 0, 255)] # Jeu de couleur du feu d'artifice

GPIO_BOUNCE_TIME = 100
GPIO_ROTARY_LEFT_A = 17
GPIO_ROTARY_LEFT_B = 27

# Effets visuels
dust_effects = []
firework_effects = []
Halo_frame_effects = []
flame_effects = []

# Pile des actions à traiter
event_actions = []

rotation_counter_left = 50
rotation_counter_right = 50

log_file = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".log"

# ####################################################
# Classes
# ####################################################

# ----------------------------------------------------
class responsive_values:
    def __init__(self, width, height):
        self.ratio = 1/6
        self.PADDLE_WIDTH = int(height*self.ratio*0.2) # Taille des raquettes
        self.PADDLE_HEIGHT = int(height*self.ratio) # Taille des raquettes
        self.PADDLE_SPEED = int(height*self.ratio*0.1) # Vitesse de deplacement des raquettes
        self.BALL_SIZE = int(height*self.ratio*0.2) # Taille de la balle
        self.BALL_INIT_SPEED = int(width*self.ratio*0.07)  # Vitesse initiale de deplacemant de la balle
        self.BALL_MAX_SPEED = int(width*self.ratio*0.15)  # Vitesse maximale de deplacemant de la balle
        self.BALL_INERTIA = int(height*self.ratio*0.09) # Inertie de la balle
        self.FONT_SIZE = int(height*self.ratio*0.8) # Taille de la police de caracteres
        self.FONT_SMALL_SIZE = int(height*self.ratio*0.4) # Taille de la police de caracteres
        self.DASH_LENGTH = int(height*self.ratio*0.1) # Definition du motif de pointille

# ----------------------------------------------------
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

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

    def move(self):
        self.x += self.vx
        self.y += self.vy
        if random.randint(0, 100) < 40:
            self.radius -= 1

# ----------------------------------------------------
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
        for particle in self.particles:
            if particle.radius > 0:
                particle.move()
            else:
                self.particles.remove(particle)
                del particle

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# ----------------------------------------------------
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

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# ----------------------------------------------------
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

    def move(self, surface, no_sound, explosion_sound):
        if not self.exploded:
            if self.direction == DIRECTION_RIGHT:
                self.x += 5
                if self.x >= random.randint(int(surface.get_width() * 0.25), int(surface.get_width() / 2 - 50)):
                    if not no_sound: pygame.mixer.Channel(2).play(explosion_sound)
                    self.exploded = True
                    self.explode()
            if self.direction == DIRECTION_LEFT:
                self.x -= 5
                if self.x <= random.randint(int(surface.get_width() / 2 + 50), int(surface.get_width() * 0.75)):
                    if not no_sound: pygame.mixer.Channel(2).play(explosion_sound)
                    self.exploded = True
                    self.explode()
        else:
            for particle in self.particles:
                particle.move()
                if particle.life <= 0:
                    self.particles.remove(particle)
                    del particle

    def draw(self, surface):
        if not self.exploded:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)
        else:
            for particle in self.particles:
                particle.draw(surface)

# ----------------------------------------------------
class Flame_particle:
    alpha_layer_qty = 2
    alpha_glow_difference_constant = 2

    def __init__(self, x, y, r=5):
        self.x = x
        self.y = y
        self.r = r
        self.original_r = r
        self.alpha_layers = Flame_particle.alpha_layer_qty
        self.alpha_glow = Flame_particle.alpha_glow_difference_constant
        max_surf_size = 2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        self.surf = pygame.Surface((max_surf_size, max_surf_size), pygame.SRCALPHA)
        self.burn_rate = 0.1 * random.randint(1, 4)

    def update(self):
        self.y -= 7 - self.r
        self.x += random.randint(-self.r, self.r)
        self.original_r -= self.burn_rate
        self.r = int(self.original_r)
        if self.r <= 0:
            self.r = 1

    def draw(self, surface, color):
        max_surf_size = 2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        self.surf = pygame.Surface((max_surf_size, max_surf_size), pygame.SRCALPHA)
        for i in range(self.alpha_layers, -1, -1):
            alpha = 255 - i * (255 // self.alpha_layers - 5)
            if alpha <= 0:
                alpha = 0
            radius = self.r * i * i * self.alpha_glow
            # multi-color mode
            # if self.r == 4 or self.r == 3:
            #     r, g, b = (255, 0, 0)
            # elif self.r == 2:
            #     r, g, b = (255, 150, 0)
            # else:
            #     r, g, b = (50, 50, 50)
            # Blue mode
            #r, g, b = (0, 0, 255)
            # White mode
            #r, g, b = (255, 255, 255)
            r, g, b = color
            color_alpha = (r, g, b, alpha)
            pygame.draw.circle(self.surf, color_alpha, (self.surf.get_width() // 2, self.surf.get_height() // 2), radius)
        surface.blit(self.surf, self.surf.get_rect(center=(self.x, self.y)))

# ----------------------------------------------------
class Flame:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.flame_intensity = 2
        self.flame_particles = []
        for i in range(self.flame_intensity * 25):
            self.flame_particles.append(Flame_particle(self.x + random.randint(-5, 5), self.y, random.randint(1, 5)))

    def draw_flame(self, surface, color):
        for i in self.flame_particles:
            if i.original_r <= 0:
                self.flame_particles.remove(i)
                self.flame_particles.append(Flame_particle(self.x + random.randint(-5, 5), self.y, random.randint(1, 5)))
                del i
                continue
            i.update()
            i.draw(surface, color)

# ----------------------------------------------------
class Halo_frame:
    def __init__(self, color, width, count, speed):
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

    def draw(self, surface, color):
        pygame.draw.line(surface, color, (0,0), (surface.get_width(),0), self.line_width)
        pygame.draw.line(surface, color, (surface.get_width(),0), (surface.get_width(),surface.get_height()), self.line_width)
        pygame.draw.line(surface, color, (surface.get_width(),surface.get_height()), (0,surface.get_height()), self.line_width)
        pygame.draw.line(surface, color, (0,surface.get_height()), (0,0), self.line_width)

# ####################################################
# Fonctions
# ####################################################

# Fonction d'aide
def help():
    print(f"""
    {Fore.RED} _______  _______  __    _  _______      _   .
    {Fore.RED}|       ||       ||  |  | ||       |    | | . _
    {Fore.MAGENTA}|    _  ||   _   ||   |_| ||    ___|    | |! |_|
    {Fore.BLUE}|   |_| ||  | |  ||       ||   | __     | | '
    {Fore.CYAN}|    ___||  |_|  ||  _    ||   ||  |    | |  '
    {Fore.GREEN}|   |    |       || | |   ||   |_| |    | |
    {Fore.YELLOW}|___|    |_______||_|  |__||_______|    |_|
    {Style.RESET_ALL}
    \033[4mParameters:\033[0m

    --help :{Style.DIM} This help message{Style.RESET_ALL}
    --no-effect :{Style.DIM} Disable visual effects{Style.RESET_ALL}
    --no-sound :{Style.DIM} Disable sound effects{Style.RESET_ALL}
    --fullscreen :{Style.DIM} Display in fullscreen{Style.RESET_ALL}
    --use-mouse :{Style.DIM} Use mouse control (useful for spinner){Style.RESET_ALL}
    --rotate-txt :{Style.DIM} Rotate texte to play face-to-face{Style.RESET_ALL}
    --use-gpio :{Style.DIM} Use GPIO (useful for Raspberry){Style.RESET_ALL}
    --help-gpio :{Style.DIM} Help on GPIO (useful for Raspberry){Style.RESET_ALL}
    --show-fps :{Style.DIM} View Framerate {Style.RESET_ALL}
    """)

# Fonction d'aide sur le connecteur GPIO
def help_gpio():
    print(f"""
        ****************************************************
        *           {Fore.CYAN}RASPBERRY Pi GPIO Connector{Style.RESET_ALL}            *
        ****************************************************
        *                                                  *
        *                    Pin 1 Pin2                    *
        *                 {Fore.MAGENTA}+3V3{Style.RESET_ALL} [ ] [ ] {Fore.RED}+5V{Style.RESET_ALL}                 *
        *       SDA1 / {Fore.GREEN}GPIO  2{Style.RESET_ALL} [ ] [ ] {Fore.RED}+5V{Style.RESET_ALL}                 *
        *       SCL1 / {Fore.GREEN}GPIO  3{Style.RESET_ALL} [ ] [ ] {Style.DIM}GND{Style.RESET_ALL}                 *
        *              {Fore.GREEN}GPIO  4{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 14{Style.RESET_ALL} / TXD0      *
        *                  {Style.DIM}GND{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 15{Style.RESET_ALL} / RXD0      *
        *              {Fore.GREEN}GPIO 17{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 18{Style.RESET_ALL}             *
        *              {Fore.GREEN}GPIO 27{Style.RESET_ALL} [ ] [ ] {Style.DIM}GND{Style.RESET_ALL}                 *
        *              {Fore.GREEN}GPIO 22{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 23{Style.RESET_ALL}             *
        *                 {Fore.MAGENTA}+3V3{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 24{Style.RESET_ALL}             *
        *       MOSI / {Fore.GREEN}GPIO 10{Style.RESET_ALL} [ ] [ ] {Style.DIM}GND{Style.RESET_ALL}                 *
        *       MISO / {Fore.GREEN}GPIO  9{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 25{Style.RESET_ALL}             *
        *       SCLK / {Fore.GREEN}GPIO 11{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO  8{Style.RESET_ALL} / CE0#      *
        *                  {Style.DIM}GND{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO  7{Style.RESET_ALL} / CE1#      *
        *      ID_SD / {Fore.GREEN}GPIO  0{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO  1{Style.RESET_ALL} / ID_SC     *
        *              {Fore.GREEN}GPIO  5{Style.RESET_ALL} [ ] [ ] {Style.DIM}GND{Style.RESET_ALL}                 *
        *              {Fore.GREEN}GPIO  6{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 12{Style.RESET_ALL}             *
        *              {Fore.GREEN}GPIO 13{Style.RESET_ALL} [ ] [ ] {Style.DIM}GND{Style.RESET_ALL}                 *
        *       MISO / {Fore.GREEN}GPIO 19{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 16{Style.RESET_ALL} / CE2#      *
        *              {Fore.GREEN}GPIO 26{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 20{Style.RESET_ALL} / MOSI      *
        *                  {Style.DIM}GND{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 21{Style.RESET_ALL} / SCLK      *
        *                   Pin 39 Pin 40                  *
        *                                                  *
        ****************************************************

    """)

# Fonction d'initialisation des interface GPIO
def rotation_decode(channel):
    global rotation_counter_left
    global rotation_counter_right

    Switch_Left_A = GPIO.input(GPIO_ROTARY_LEFT_A)
    Switch_Left_B = GPIO.input(GPIO_ROTARY_LEFT_B)

    logging.info('--------------------------------')
    logging.info('Switch_Left_A %s' % Switch_Left_A)
    logging.info('Switch_Left_B %s' % Switch_Left_B)

    if (Switch_Left_A == 1) and (Switch_Left_B == 0):
        rotation_counter_left += 1
        event_actions.append("LEFT_PADDLE_UP")
        logging.info('direction -> %s' % rotation_counter_left)
        while Switch_Left_B == 0:
            Switch_Left_B = GPIO.input(GPIO_ROTARY_LEFT_B)
        while Switch_Left_B == 1:
            Switch_Left_B = GPIO.input(GPIO_ROTARY_LEFT_B)
        return

    elif (Switch_Left_A == 1) and (Switch_Left_B == 1):
        rotation_counter_left -= 1
        event_actions.append("LEFT_PADDLE_DOWN")
        logging.info('direction <- %s' % rotation_counter_left)
        while Switch_Left_A == 1:
            Switch_Left_A = GPIO.input(GPIO_ROTARY_LEFT_A)
        return
    else:
        return

# Fonction d'initialisation des interface GPIO
def init_GPIO():
    logging.info("Rotary Encoder Test Program")
    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_ROTARY_LEFT_A, GPIO.IN)
    GPIO.setup(GPIO_ROTARY_LEFT_B, GPIO.IN)
    GPIO.add_event_detect(GPIO_ROTARY_LEFT_A, GPIO.BOTH, rotation_decode, GPIO_BOUNCE_TIME)
    #GPIO.add_event_detect(GPIO_ROTARY_LEFT_A, GPIO.BOTH, rotation_decode)
    # GPIO.add_event_detect(GPIO_ROTARY_LEFT_A, GPIO.BOTH)
    # GPIO.add_event_callback(GPIO_ROTARY_LEFT_A, rotation_decode)
    #– BOTH, déclenche l’interrupt quand le pin change d’état ( de bas à haut , ou de haut à bas )
    #– RISING, sur front montant, il se déclenche seulement quand on va passer d’un état bas à haut
    #– FALLING, sur front descendant, il se déclenche seulement quand on va passer d’un état haut à bas
    return

# Fonction pour dessiner les raquettes
def draw_paddles(surface, color, left_paddle_y, right_paddle_y, paddle_with, paddle_height, line_width):
    pygame.draw.rect(surface, color, (int(line_width), int(left_paddle_y - paddle_height / 2) , paddle_with, paddle_height))
    pygame.draw.rect(surface, color, (int(surface.get_width() - paddle_with - line_width), int(right_paddle_y - paddle_height / 2), paddle_with, paddle_height))

# Fonction pour dessiner la balle
def draw_ball(surface, color, ball_x, ball_y, size):
    pygame.draw.rect(surface, color, (int(ball_x-size/2), int(ball_y-size/2), int(size), int(size)))

# Fonction pour afficher le FPS
def draw_fps(surface, color, font, text):
        text = font.render(text, True, color)
        surface.blit(text, (10, 10))

# Fonction pour afficher le score
def draw_score(surface, color, font, font_size, rotate_txt, left_score, right_score):
    left_text = font.render(str(left_score), True, color)
    right_text = font.render(str(right_score), True, color)
    if rotate_txt:
        left_text = pygame.transform.rotate(left_text, 270)
        right_text = pygame.transform.rotate(right_text, 90)
        surface.blit(left_text, (int(surface.get_width() / 2 - (font_size + 20)), 20))
        surface.blit(right_text, (int(surface.get_width() / 2 + 20), 20))
    else:
        surface.blit(left_text, (int(surface.get_width() / 2 - (font_size/2 + 20)), 10))
        surface.blit(right_text, (int(surface.get_width() / 2 + 20), 10))

# Fonction pour afficher le texte de fin de jeu
def draw_endgame(surface, color, font, font_size, rotate_txt, left_score, right_score):
    # Victoire a gauche
    if left_score >= WIN_SCORE:
        looser_text = font.render(LOOSE_TXT, True, color)
        winner_text = font.render(WIN_TXT, True, color)
        if rotate_txt:
            looser_text = pygame.transform.rotate(looser_text, 90)
            surface.blit(looser_text, (int(surface.get_width() * 0.75 - font_size / 2), int(surface.get_height() / 2 - (len(LOOSE_TXT) * font_size / 4)) ))
            winner_text = pygame.transform.rotate(winner_text, 270)
            surface.blit(winner_text, (int(surface.get_width() * 0.25 - font_size / 2), int(surface.get_height() / 2 - (len(WIN_TXT) * font_size / 4)) ))
        else:
            surface.blit(looser_text, (int(surface.get_width() * 0.75 - (len(LOOSE_TXT) * font_size / 4)), int(surface.get_height() / 2 - (font_size / 2)) ))
            surface.blit(winner_text, (int(surface.get_width() * 0.25 - (len(WIN_TXT) * font_size / 4)), int(surface.get_height() / 2 - (font_size / 2)) ))
    # Victoire a droite
    if right_score >= WIN_SCORE:
        winner_text = font.render(WIN_TXT, True, color)
        looser_text = font.render(LOOSE_TXT, True, color)
        if rotate_txt:
            winner_text = pygame.transform.rotate(winner_text, 90)
            surface.blit(winner_text, (int(surface.get_width() * 0.75 - font_size / 2), int(surface.get_height() / 2 - (len(WIN_TXT) * font_size / 4)) ))
            looser_text = pygame.transform.rotate(looser_text, 270)
            surface.blit(looser_text, (int(surface.get_width() * 0.25 - font_size / 2), int(surface.get_height() / 2 - (len(LOOSE_TXT) * font_size / 4)) ))
        else:
            surface.blit(winner_text, (int(surface.get_width() * 0.75 - (len(WIN_TXT) * font_size / 4)), int(surface.get_height() / 2 - (font_size / 2)) ))
            surface.blit(looser_text, (int(surface.get_width() * 0.25 - (len(LOOSE_TXT) * font_size / 4)), int(surface.get_height() / 2 - (font_size / 2)) ))

# Fonction pour afficher une ligne en pointilles
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

# Fonction pour afficher la cadre de jeu
def draw_frame(surface, color, width=1):
    pygame.draw.line(surface, color, (0,0), (surface.get_width(),0), width)
    pygame.draw.line(surface, color, (surface.get_width(),0), (surface.get_width(),surface.get_height()), width)
    pygame.draw.line(surface, color, (surface.get_width(),surface.get_height()), (0,surface.get_height()), width)
    pygame.draw.line(surface, color, (0,surface.get_height()), (0,0), width)

# ####################################################
# Fonction principale
# ####################################################

def main():

    current_player = random.randint(1, 2)
    clock = pygame.time.Clock()

    # Controle des parametres d'entree
    no_effect = False
    no_sound = False
    fullscreen = False
    use_mouse = False
    use_gpio = False
    rotate_txt = False
    show_fps = False
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            if "--no-effect" in sys.argv[i]:
                logging.info("argument : no-effect")
                no_effect = True
            elif "--no-sound" in sys.argv[i]:
                logging.info("argument : no-sound")
                no_sound = True
            elif "--use-mouse" in sys.argv[i]:
                logging.info("argument : use-mouse")
                use_mouse = True
            elif "--use-gpio" in sys.argv[i]:
                logging.info("argument : use-gpio")
                use_gpio = True
            elif "--rotate-txt" in sys.argv[i]:
                logging.info("argument : rotate-txt")
                rotate_txt = True
            elif "--help-gpio" in sys.argv[i]:
                logging.info("argument : help-gpio")
                help_gpio()
                sys.exit()
            elif "--show-fps" in sys.argv[i]:
                logging.info("argument : show-fps")
                show_fps = True
            elif "--fullscreen" in sys.argv[i]:
                logging.info("argument : fullscreen")
                fullscreen = True
            else:
                help()
                sys.exit()

    # Initialisation des interface GPIO
    if use_gpio:
        if _rpi_gpio_Loaded:
            init_GPIO()
        else:
            logging.warning("no GPIO found")

    # Chargement des effets sonores
    if not no_sound:
        pygame.mixer.set_num_channels(3)
        bundle_sound_dir = getattr(sys, '_MEIPASS', "sfx") # Check if MEIPASS attribute is available in sys else return current file path
        paddle_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'paddle.wav')))
        wall_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'wall.wav')))
        score_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'score.wav')))
        start_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'start.wav')))
        gameover_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'gameover.wav')))
        laser_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'laser.wav')))
        explosion_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'explosion.wav')))

    # Definition du mode d'affichage
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
    else:
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pong")
        bundle_image_dir = getattr(sys, '_MEIPASS', "image") # Check if MEIPASS attribute is available in sys else return current file path
        icon = pygame.image.load(os.path.abspath(os.path.join(bundle_image_dir,'logo.png'))).convert_alpha()
        pygame.display.set_icon(icon)

    # Calcul des valeurs relatives en fonction de la resolution
    responsive = responsive_values(screen.get_width(), screen.get_height())

    # chargement de la police de caracteres
    bundle_font_dir = getattr(sys, '_MEIPASS', "font") # Check if MEIPASS attribute is available in sys else return current file path
    path_to_font = os.path.abspath(os.path.join(bundle_font_dir,'SevenSegment.ttf'))
    font = pygame.font.Font(path_to_font, responsive.FONT_SIZE)
    font_small = pygame.font.Font(path_to_font, responsive.FONT_SMALL_SIZE)

    # Valeurs initiales
    left_score = 0
    right_score = 0
    game_started = False
    game_paused = False
    ball_replace_timer = 0
    previous_mouse_position = pygame.mouse.get_pos()
    ball_replace_timer = 0
    last_ball_x_position = 0
    last_ball_y_position = 0
    ball_speed = responsive.BALL_INIT_SPEED
    ball_speed_x = 0
    ball_speed_y = 0
    left_accerlerate_paddle = False
    right_accerlerate_paddle = False
    ball_in_fire = False
    main_color = WHITE

    # Initialisation de la position des raquettes
    left_paddle_y = screen.get_height() / 2
    right_paddle_y = screen.get_height() / 2

    # Initialisation de la position de la balle
    if ( current_player == 1 ):
        ball_x = responsive.PADDLE_WIDTH + SPACE_WIDTH + responsive.BALL_SIZE / 2 + LINE_WIDTH
        ball_y = left_paddle_y
    elif ( current_player == 2 ):
        ball_x = screen.get_width() - responsive.PADDLE_WIDTH - SPACE_WIDTH - responsive.BALL_SIZE / 2 - LINE_WIDTH
        ball_y = right_paddle_y

    running = True

    if not no_sound: pygame.mixer.Channel(0).play(start_sound)

    while running:

        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                event_actions.append("EXIT")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    event_actions.append("EXIT")
                if event.key == pygame.K_r:
                    event_actions.append("RESET")
                if event.key == pygame.K_LCTRL:
                    event_actions.append("LEFT_PADDLE_BUTTON")
                if event.key == pygame.K_RCTRL:
                    event_actions.append("RIGHT_PADDLE_BUTTON")
            if event.type == pygame.MOUSEBUTTONDOWN and use_mouse == True:
                # Barre gauche - click gauche
                if event.button == 1:
                    event_actions.append("LEFT_PADDLE_BUTTON")
                # click central
                elif event.button == 2:
                    event_actions.append("RESET")
                # Barre droite - click droite
                elif event.button == 3:
                    event_actions.append("RIGHT_PADDLE_BUTTON")
            if event.type == pygame.MOUSEMOTION and use_mouse == True:
                # Recuperation de la position du curseur
                mouse_position=event.pos
                # Barre gauche - mouvement horizontal
                if mouse_position[0] < previous_mouse_position[0]:
                    event_actions.append("LEFT_PADDLE_UP")
                elif mouse_position[0] > previous_mouse_position[0]:
                    event_actions.append("LEFT_PADDLE_DOWN")
                # Barre droite - mouvement vetical
                if mouse_position[1] < previous_mouse_position[1]:
                    event_actions.append("RIGHT_PADDLE_UP")
                elif mouse_position[1] > previous_mouse_position[1]:
                    event_actions.append("RIGHT_PADDLE_DOWN")
                # Enregistrement de la position du curseur
                previous_mouse_position=event.pos

        keys = pygame.key.get_pressed()
        if game_paused == False:
            if keys[pygame.K_w] or keys[pygame.K_z]:
                event_actions.append("LEFT_PADDLE_UP")
            if keys[pygame.K_s]:
                event_actions.append("LEFT_PADDLE_DOWN")
            if keys[pygame.K_UP]:
                event_actions.append("RIGHT_PADDLE_UP")
            if keys[pygame.K_DOWN]:
                event_actions.append("RIGHT_PADDLE_DOWN")
            if keys[pygame.K_LCTRL]:
                left_accerlerate_paddle = True
            if keys[pygame.K_RCTRL]:
                right_accerlerate_paddle = True

        for action in event_actions:
            # --------------------------------------------------------------------------------------------------
            if action == "LEFT_PADDLE_UP":
                if left_paddle_y >= LINE_WIDTH + SPACE_WIDTH + responsive.PADDLE_HEIGHT / 2:
                    if abs(left_paddle_y - (LINE_WIDTH + SPACE_WIDTH + responsive.PADDLE_HEIGHT / 2)) < responsive.PADDLE_SPEED:
                        left_paddle_y = LINE_WIDTH + responsive.PADDLE_HEIGHT / 2
                    else:
                        if left_accerlerate_paddle == True :
                            left_paddle_y -= responsive.PADDLE_SPEED * 2
                            left_accerlerate_paddle = False
                        else:
                            left_paddle_y -= responsive.PADDLE_SPEED
            # --------------------------------------------------------------------------------------------------
            elif action == "LEFT_PADDLE_DOWN":
                if left_paddle_y <= screen.get_height() - LINE_WIDTH - SPACE_WIDTH - responsive.PADDLE_HEIGHT / 2:
                    if abs(left_paddle_y - (screen.get_height() - LINE_WIDTH - SPACE_WIDTH - responsive.PADDLE_HEIGHT / 2)) < responsive.PADDLE_SPEED:
                        left_paddle_y = screen.get_height() - LINE_WIDTH - responsive.PADDLE_HEIGHT / 2
                    else:
                        if left_accerlerate_paddle == True :
                            left_paddle_y += responsive.PADDLE_SPEED * 2
                            left_accerlerate_paddle = False
                        else:
                            left_paddle_y += responsive.PADDLE_SPEED
            # --------------------------------------------------------------------------------------------------
            elif action == "RIGHT_PADDLE_UP":
                if right_paddle_y >= LINE_WIDTH + SPACE_WIDTH + responsive.PADDLE_HEIGHT / 2:
                    if abs(right_paddle_y - (LINE_WIDTH + SPACE_WIDTH + responsive.PADDLE_HEIGHT / 2)) < responsive.PADDLE_SPEED:
                        right_paddle_y = LINE_WIDTH + responsive.PADDLE_HEIGHT / 2
                    else:
                        if right_accerlerate_paddle == True :
                            right_paddle_y -= responsive.PADDLE_SPEED * 2
                            right_accerlerate_paddle = False
                        else:
                            right_paddle_y -= responsive.PADDLE_SPEED
            # --------------------------------------------------------------------------------------------------
            elif action == "RIGHT_PADDLE_DOWN":
                if right_paddle_y <= screen.get_height() - LINE_WIDTH - SPACE_WIDTH - responsive.PADDLE_HEIGHT / 2:
                    if abs(right_paddle_y - (screen.get_height() - LINE_WIDTH - SPACE_WIDTH - responsive.PADDLE_HEIGHT / 2)) < responsive.PADDLE_SPEED:
                        right_paddle_y = screen.get_height() - LINE_WIDTH - responsive.PADDLE_HEIGHT / 2
                    else:
                        if right_accerlerate_paddle == True :
                            right_paddle_y += responsive.PADDLE_SPEED * 2
                            right_accerlerate_paddle = False
                        else:
                            right_paddle_y += responsive.PADDLE_SPEED
            # --------------------------------------------------------------------------------------------------
            elif action == "LEFT_PADDLE_BUTTON":
                if not game_started and not game_paused:
                    # re-initialisation des scores
                    if right_score >= WIN_SCORE:
                        right_score = 0
                        left_score = 0
                    # Lancement de la balle a droite
                    if ( current_player == 1 ):
                        if not no_effect: dust_effects.append(Dust(ball_x-responsive.BALL_SIZE / 2, ball_y, main_color, DIRECTION_RIGHT))
                        # Calcul de l'angle de rebond base sur la position relative de la balle sur la raquette
                        relative_intersect_y = left_paddle_y - ball_y
                        normalized_intersect_y = relative_intersect_y / (responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2)
                        bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degres)
                        ball_speed_x = ball_speed * math.cos(bounce_angle)
                        ball_speed_y = ball_speed * -math.sin(bounce_angle)
                        game_started = True
                    # Lancement de la balle a droite
                    if ( current_player == 2  and left_score >= WIN_SCORE ):
                        if not no_effect:
                            if not no_sound: pygame.mixer.Channel(1).play(laser_sound)
                            firework_color = random.choice(FIREWORK_COLORS)
                            firework_effects.append(Firework(responsive.PADDLE_WIDTH + SPACE_WIDTH, left_paddle_y, firework_color, DIRECTION_RIGHT))
                            dust_effects.append(Dust(responsive.PADDLE_WIDTH + SPACE_WIDTH, left_paddle_y, firework_color, DIRECTION_RIGHT))
            # --------------------------------------------------------------------------------------------------
            elif action == "RIGHT_PADDLE_BUTTON":
                if not game_started and not game_paused:
                    # re-initialisation des scores
                    if left_score >= WIN_SCORE:
                        right_score = 0
                        left_score = 0
                    # Lancement de la balle a gauche
                    if ( current_player == 2 ):
                        if not no_effect: dust_effects.append(Dust(ball_x+responsive.BALL_SIZE / 2, ball_y, main_color, DIRECTION_LEFT))
                        # Calcul de l'angle de rebond base sur la position relative de la balle sur la raquette
                        relative_intersect_y = right_paddle_y - ball_y
                        normalized_intersect_y = relative_intersect_y / (responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2)
                        bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degres)
                        ball_speed_x = -ball_speed * math.cos(bounce_angle)
                        ball_speed_y = ball_speed * -math.sin(bounce_angle)
                        game_started = True
                    if ( current_player == 1 and right_score >= WIN_SCORE):
                        if not no_effect:
                            if not no_sound: pygame.mixer.Channel(1).play(laser_sound)
                            firework_color = random.choice(FIREWORK_COLORS)
                            firework_effects.append(Firework(screen.get_width() - responsive.PADDLE_WIDTH - SPACE_WIDTH, right_paddle_y, firework_color, DIRECTION_LEFT))
                            dust_effects.append(Dust(screen.get_width() - responsive.PADDLE_WIDTH - SPACE_WIDTH, right_paddle_y, firework_color, DIRECTION_LEFT))
            # --------------------------------------------------------------------------------------------------
            elif action == "RESET":
                right_score = 0
                left_score = 0
                ball_speed = responsive.BALL_INIT_SPEED
                ball_in_fire = False
            # --------------------------------------------------------------------------------------------------
            elif action == "EXIT":
                running = False
            # --------------------------------------------------------------------------------------------------
            event_actions.remove(action) # Purge de l'action

        if game_started == True:

            ball_x += ball_speed_x
            ball_y += ball_speed_y

            # rebond de la balle sur le haut
            if ball_y <= responsive.BALL_SIZE/2:
                if not no_sound: pygame.mixer.Channel(2).play(wall_sound)
                ball_speed_y = -ball_speed_y
                if not no_effect: dust_effects.append(Dust(ball_x, ball_y - responsive.BALL_SIZE/2, main_color, DIRECTION_DOWN))

            # rebond de la balle sur la bas
            if ball_y >= screen.get_height() - responsive.BALL_SIZE/2:
                if not no_sound: pygame.mixer.Channel(2).play(wall_sound)
                ball_speed_y = -ball_speed_y
                if not no_effect: dust_effects.append(Dust(ball_x, ball_y + responsive.BALL_SIZE/2, main_color, DIRECTION_UP))

            # rebond de la balle sur la raquette gauche
            if ball_x <= LINE_WIDTH + SPACE_WIDTH + responsive.PADDLE_WIDTH + responsive.BALL_SIZE / 2 and left_paddle_y - responsive.PADDLE_HEIGHT / 2 - responsive.BALL_SIZE / 2 < ball_y < left_paddle_y + responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2 :
                if not no_sound: pygame.mixer.Channel(1).play(paddle_sound)
                ball_speed += BALL_ACCELERATION * (1 if ball_speed > 0 else -1)  # Augmentation de la vitesse
                ball_speed = max(min(ball_speed, responsive.BALL_MAX_SPEED), -responsive.BALL_MAX_SPEED) # Vitesse maximale
                if abs(ball_speed) >= responsive.BALL_MAX_SPEED and ball_in_fire == False:
                    if not no_effect: flame_effects.append(Flame(ball_x, ball_y + responsive.BALL_SIZE/2))
                    ball_in_fire = True
                ball_speed_x = -ball_speed_x
                if ball_x < LINE_WIDTH + SPACE_WIDTH + responsive.PADDLE_WIDTH + responsive.BALL_SIZE / 2:
                    ball_x = LINE_WIDTH + SPACE_WIDTH + responsive.PADDLE_WIDTH + responsive.BALL_SIZE / 2
                if not no_effect: dust_effects.append(Dust(ball_x - responsive.BALL_SIZE / 2, ball_y, main_color, DIRECTION_RIGHT))
                # Calcul de l'angle de rebond base sur la position relative de la balle sur la raquette
                relative_intersect_y = left_paddle_y - ball_y
                normalized_intersect_y = relative_intersect_y / (responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2)
                bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degres)
                ball_speed_x = ball_speed * math.cos(bounce_angle)
                ball_speed_y = ball_speed * -math.sin(bounce_angle)

            # rebond de la balle sur la raquette droite
            if ball_x >= screen.get_width() - LINE_WIDTH - SPACE_WIDTH - responsive.PADDLE_WIDTH - responsive.BALL_SIZE / 2 and right_paddle_y  - responsive.PADDLE_HEIGHT / 2 - responsive.BALL_SIZE / 2 < ball_y < right_paddle_y + responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2:
                if not no_sound: pygame.mixer.Channel(1).play(paddle_sound)
                ball_speed += BALL_ACCELERATION * (1 if ball_speed > 0 else -1)  # Augmentation de la vitesse
                ball_speed = max(min(ball_speed, responsive.BALL_MAX_SPEED), -responsive.BALL_MAX_SPEED) # Vitesse maximale
                if abs(ball_speed) >= responsive.BALL_MAX_SPEED and ball_in_fire == False:
                    if not no_effect: flame_effects.append(Flame(ball_x, ball_y + responsive.BALL_SIZE/2))
                    ball_in_fire = True
                ball_speed_x = -ball_speed_x
                if ball_x > screen.get_width() - LINE_WIDTH - SPACE_WIDTH - responsive.PADDLE_WIDTH - responsive.BALL_SIZE / 2:
                    ball_x = screen.get_width() - LINE_WIDTH - SPACE_WIDTH - responsive.PADDLE_WIDTH - responsive.BALL_SIZE / 2
                if not no_effect: dust_effects.append(Dust(ball_x + responsive.BALL_SIZE / 2, ball_y, main_color, DIRECTION_LEFT))
                # Calcul de l'angle de rebond base sur la position relative de la balle sur la raquette
                relative_intersect_y = right_paddle_y - ball_y
                normalized_intersect_y = relative_intersect_y / (responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2)
                bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degres)
                ball_speed_x = -ball_speed * math.cos(bounce_angle)
                ball_speed_y = ball_speed * -math.sin(bounce_angle)

            # Sortie de la balle a gauche
            if ball_x <= LINE_WIDTH + SPACE_WIDTH + responsive.BALL_SIZE / 2:
                right_score += 1
                if right_score < WIN_SCORE:
                    if not no_sound: pygame.mixer.Channel(0).play(score_sound)
                else:
                    if not no_sound: pygame.mixer.Channel(0).play(gameover_sound)
                last_ball_x_position = ball_x
                last_ball_y_position = ball_y
                ball_speed_x = 0
                ball_speed_y = 0
                game_started = False
                game_paused = True
                ball_replace_timer = BALL_REPLACE_DURATION
                current_player = 1
                if not no_effect: Halo_frame_effects.append(Halo_frame(main_color, HALO_FRAME_WIDTH, HALO_FRAME_COUNT, HALO_FRAME_SPEED))
                if right_score >= WIN_SCORE:
                    ball_speed = responsive.BALL_INIT_SPEED
                    ball_in_fire = False
                    game_started = False

            # Sortie de la balle a droite
            if ball_x >= screen.get_width() - LINE_WIDTH - SPACE_WIDTH - responsive.BALL_SIZE / 2:
                left_score += 1
                if left_score < WIN_SCORE:
                    if not no_sound: pygame.mixer.Channel(0).play(score_sound)
                else:
                    if not no_sound: pygame.mixer.Channel(0).play(gameover_sound)
                last_ball_x_position = ball_x
                last_ball_y_position = ball_y
                ball_speed_x = 0
                ball_speed_y = 0
                game_started = False
                game_paused = True
                ball_replace_timer = BALL_REPLACE_DURATION
                current_player = 2
                if not no_effect: Halo_frame_effects.append(Halo_frame(main_color, HALO_FRAME_WIDTH, HALO_FRAME_COUNT, HALO_FRAME_SPEED))
                if left_score >= WIN_SCORE:
                    ball_speed = responsive.BALL_INIT_SPEED
                    ball_in_fire = False
                    game_started = False

        else:

            if game_paused == False:

                # Suivi de la balle sur la raquette
                ball_speed_x = 0
                ball_speed_y = 0
                if ( current_player == 1 ):
                    ball_x = responsive.PADDLE_WIDTH + SPACE_WIDTH + responsive.BALL_SIZE / 2 + LINE_WIDTH
                    if abs(ball_y - left_paddle_y) < responsive.BALL_INERTIA: ball_y = left_paddle_y
                    if ball_y < left_paddle_y: ball_y += responsive.BALL_INERTIA
                    if ball_y > left_paddle_y: ball_y -= responsive.BALL_INERTIA
                    if ball_y < left_paddle_y - responsive.PADDLE_HEIGHT / 2: ball_y = left_paddle_y - responsive.PADDLE_HEIGHT / 2
                    if ball_y > left_paddle_y + responsive.PADDLE_HEIGHT / 2: ball_y = left_paddle_y + responsive.PADDLE_HEIGHT / 2
                elif ( current_player == 2 ):
                    ball_x = screen.get_width() - responsive.PADDLE_WIDTH - SPACE_WIDTH - responsive.BALL_SIZE / 2 - LINE_WIDTH
                    if abs(ball_y - right_paddle_y) < responsive.BALL_INERTIA: ball_y = right_paddle_y
                    if ball_y < right_paddle_y: ball_y += responsive.BALL_INERTIA
                    if ball_y > right_paddle_y: ball_y -= responsive.BALL_INERTIA
                    if ball_y < right_paddle_y - responsive.PADDLE_HEIGHT / 2: ball_y = right_paddle_y - responsive.PADDLE_HEIGHT / 2
                    if ball_y > right_paddle_y + responsive.PADDLE_HEIGHT / 2: ball_y = right_paddle_y + responsive.PADDLE_HEIGHT / 2

        # Replacement de la balle
        if game_paused == True and ball_replace_timer > 0:
            ball_replace_timer -= 1
            percent = ball_replace_timer / BALL_REPLACE_DURATION
            if current_player == 1:
                ball_x = (responsive.PADDLE_WIDTH + SPACE_WIDTH + responsive.BALL_SIZE / 2 + LINE_WIDTH) - (((responsive.PADDLE_WIDTH + SPACE_WIDTH + responsive.BALL_SIZE / 2) - last_ball_x_position) * percent)
                ball_y = left_paddle_y - ((left_paddle_y - last_ball_y_position) * percent)
            if current_player == 2:
                ball_x = (screen.get_width() - responsive.PADDLE_WIDTH - SPACE_WIDTH - responsive.BALL_SIZE / 2 - LINE_WIDTH) - (((screen.get_width() - responsive.PADDLE_WIDTH - SPACE_WIDTH - responsive.BALL_SIZE / 2) - last_ball_x_position) * percent)
                ball_y = right_paddle_y - ((right_paddle_y - last_ball_y_position) * percent)

        # Reprise du jeu
        if game_paused == True and ball_replace_timer <= 0:
            game_paused = False

        # Mise a jour et dessin des effets de particules
        for particle in dust_effects:
            if len(particle.particles) > 0:
                particle.update()
                particle.draw(screen)
            else:
                dust_effects.remove(particle)
                del particle

        for firework in firework_effects:
            if len(firework.particles) > 0 or firework.exploded == False:
                firework.move(screen, no_sound, explosion_sound)
                firework.draw(screen)
            else:
                firework_effects.remove(firework)
                del firework

        for flame in flame_effects:
            if ball_speed >= responsive.BALL_MAX_SPEED:
                flame.x = ball_x
                flame.y = ball_y + responsive.BALL_SIZE/2
                flame.draw_flame(screen, main_color)
            else:
                flame_effects.remove(flame)
                del flame

        for halo in Halo_frame_effects:
            if halo.count > 0:
                halo.move()
                halo.draw(screen, main_color)
            else:
                Halo_frame_effects.remove(halo)
                del halo

        draw_frame(screen, main_color, LINE_WIDTH)
        draw_dashed_line(screen, main_color, (screen.get_width() / 2, 0), (screen.get_width() / 2, screen.get_height()), LINE_WIDTH, responsive.DASH_LENGTH)
        draw_paddles(screen, main_color, left_paddle_y, right_paddle_y, responsive.PADDLE_WIDTH, responsive.PADDLE_HEIGHT, LINE_WIDTH)
        draw_ball(screen, main_color, ball_x, ball_y, responsive.BALL_SIZE)
        draw_score(screen, main_color, font, responsive.FONT_SIZE, rotate_txt, left_score, right_score)
        draw_endgame(screen, main_color, font, responsive.FONT_SIZE, rotate_txt, left_score, right_score)
        if show_fps: draw_fps(screen, main_color, font_small, str(int(clock.get_fps())))

        pygame.display.flip()

        # Limiter la vitesse de la boucle a 60 FPS
        clock.tick(60)

    pygame.quit()

# ####################################################
# Launch main
# ####################################################

if __name__ == "__main__":
    try:
        if os.path.exists(log_file): os.remove(log_file) # Supprime le fichier de trace précédent
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
        logging.info('----------------------------------------')
        logging.info('system  : %s' % platform.system())
        logging.info('machine : %s' % platform.machine())
        logging.info('CPU     : %s' % os.cpu_count())
        logging.info('os      : %s' % platform.platform())
        logging.info('python  : %s' % platform.python_version())
        logging.info('pygame  : %s' % pygame.ver)
        logging.info('----------------------------------------')
        colorama.init()
        main()
    except Exception:
        help()
        print(traceback.format_exc())
        logging.error(traceback.format_exc())
        sys.exit()
