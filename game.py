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
import asyncio
import time
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
BALL_ACCELERATION = 10 # Acceleration de la balle a chaque rebond
BALL_REPLACE_DURATION = 300 # Temps de replacement de la balle sur la raquette
HALO_FRAME_COUNT = 2 # Nombre de flash du halo
HALO_FRAME_SPEED = 5 # Vitesse du halo
HALO_FRAME_WIDTH = 15 # epaisseur maximale du halo
WIN_SCORE = 8 # Score a obtenir pour gagner
MAX_FPS = 100 # Vitesse de rafraichessement maximum
EFFECT_FPS = 60 # Vitesse de l'animation
WIDTH, HEIGHT = 800, 600 # Resolution d'affichage
FIREWORK_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (255, 192, 203), (255, 0, 255)] # Jeu de couleur du feu d'artifice
PADDLE_DECELERATE_MOUSE = 50 # Facteur de desceleration de la vitesse de déplacement des raquettes à la souris

# GPIO_BOUNCE_TIME = 100
# GPIO_ROTARY_LEFT_A = 17
# GPIO_ROTARY_LEFT_B = 27
GPIO_BUTTON_LEFT = 23 # Port GPIO du bouton du joueur de gauche
GPIO_BUTTON_RIGHT = 25 # Port GPIO du bouton du joueur de droite
GPIO_BUTTON_RESET = 12 # Port GPIO du bouton reset
GPIO_BUTTON_RIGHT_EVENT = pygame.USEREVENT + 1 # Evenement personnalisé du bouton du joueur de gauche
GPIO_BUTTON_LEFT_EVENT = pygame.USEREVENT + 2 # Evenement personnalisé du bouton du joueur de droite
GPIO_BUTTON_RESET_EVENT = pygame.USEREVENT + 3 # Evenement personnalisé du bouton reset

# Effets visuels
dust_effects = []
firework_effects = []
Halo_frame_effects = []
shiny_effects = []

# Pile des actions à traiter
event_actions = []

rotation_counter_left = 50
rotation_counter_right = 50

log_file = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".log"

# ############################################################################################################################################################
# Classes
# ############################################################################################################################################################

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class responsive_values
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
class responsive_values:
    def __init__(self, width, height):
        self.ratio = 1/6
        self.PADDLE_WIDTH = int(height*self.ratio*0.2) # Taille des raquettes
        self.PADDLE_HEIGHT = int(height*self.ratio) # Taille des raquettes
        self.PADDLE_SPEED_KEYBOARD = int(height*self.ratio*10) # Vitesse de deplacement des raquettes avec le clavier
        self.PADDLE_SPEED_MOUSE = int(height*self.ratio/3.5) # Vitesse de deplacement des raquettes avec la souris
        self.BALL_SIZE = int(height*self.ratio*0.2) # Taille de la balle
        self.BALL_INIT_SPEED = int(width*self.ratio*6)  # Vitesse initiale de deplacemant de la balle
        self.BALL_MAX_SPEED = int(width*self.ratio*10)  # Vitesse maximale de deplacemant de la balle
        self.BALL_INERTIA = int(height*self.ratio*0.06) # Inertie de suivi de la balle sur la raquette
        self.FONT_LARGE_SIZE = int(height*self.ratio*0.8) # Taille de la police de caracteres large
        self.FONT_SMALL_SIZE = int(height*self.ratio*0.4) # Taille de la police de caracteres petite
        self.DASH_LENGTH = int(height*self.ratio*0.1) # Definition du motif de pointille

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class application_values
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
class application_values:
    def __init__(self, surface, responsive):
        self.main_color = WHITE
        # ------------------------
        self._game_started = False
        self._game_paused = False
        self._current_player = random.randint(1, 2)
        self._ball_speed = responsive.BALL_INIT_SPEED
        self._ball_speed_x = 0
        self._ball_speed_y = 0
        self._left_score = 0
        self._right_score = 0
        self._ball_replace_timer = 0
        self._registered_ball_x_position = 0
        self._registered_ball_y_position = 0
        self._ball_in_fire = False
        self._left_paddle_move = "NONE"
        self._right_paddle_move = "NONE"

        # Initialisation de la position des raquettes
        self._left_paddle_y = surface.get_height() / 2
        self._right_paddle_y = surface.get_height() / 2

        # Initialisation de la position de la balle
        if ( self._current_player == 1 ):
            self._ball_x = responsive.PADDLE_WIDTH + SPACE_WIDTH + responsive.BALL_SIZE / 2 + LINE_WIDTH
            self._ball_y = self._left_paddle_y
        elif ( self._current_player == 2 ):
            self._ball_x = surface.get_width() - responsive.PADDLE_WIDTH - SPACE_WIDTH - responsive.BALL_SIZE / 2 - LINE_WIDTH
            self._ball_y = self._right_paddle_y

    @property
    def current_player(self): return self._current_player
    @current_player.setter
    def current_player(self, value): self._current_player = value

    @property
    def game_started(self): return self._game_started
    @game_started.setter
    def game_started(self, value): self._game_started = value

    @property
    def game_paused(self): return self._game_paused
    @game_paused.setter
    def game_paused(self, value): self._game_paused = value

    @property
    def left_score(self): return self._left_score
    @left_score.setter
    def left_score(self, value): self._left_score = value

    @property
    def right_score(self): return self._right_score
    @right_score.setter
    def right_score(self, value): self._right_score = value

    @property
    def ball_replace_timer(self): return self._ball_replace_timer
    @ball_replace_timer.setter
    def ball_replace_timer(self, value): self._ball_replace_timer = value

    @property
    def ball_in_fire(self): return self._ball_in_fire
    @ball_in_fire.setter
    def ball_in_fire(self, value): self._ball_in_fire = value

    @property
    def ball_speed(self): return self._ball_speed
    @ball_speed.setter
    def ball_speed(self, value): self._ball_speed = value

    @property
    def ball_speed_x(self): return self._ball_speed_x
    @ball_speed_x.setter
    def ball_speed_x(self, value): self._ball_speed_x = value

    @property
    def ball_speed_y(self): return self._ball_speed_y
    @ball_speed_y.setter
    def ball_speed_y(self, value): self._ball_speed_y = value

    @property
    def ball_x(self): return self._ball_x
    @ball_x.setter
    def ball_x(self, value): self._ball_x = value

    @property
    def ball_y(self): return self._ball_y
    @ball_y.setter
    def ball_y(self, value): self._ball_y = value

    @property
    def registered_ball_x_position(self): return self._registered_ball_x_position
    @registered_ball_x_position.setter
    def registered_ball_x_position(self, value): self._registered_ball_x_position = value

    @property
    def registered_ball_y_position(self): return self._registered_ball_y_position
    @registered_ball_y_position.setter
    def registered_ball_y_position(self, value): self._registered_ball_y_position = value

    @property
    def right_paddle_y(self): return self._right_paddle_y
    @right_paddle_y.setter
    def right_paddle_y(self, value): self._right_paddle_y = value

    @property
    def left_paddle_y(self): return self._left_paddle_y
    @left_paddle_y.setter
    def left_paddle_y(self, value): self._left_paddle_y = value

    @property
    def right_paddle_move(self): return self._right_paddle_move
    @right_paddle_move.setter
    def right_paddle_move(self, value): self._right_paddle_move = value

    @property
    def left_paddle_move(self): return self._left_paddle_move
    @left_paddle_move.setter
    def left_paddle_move(self, value): self._left_paddle_move = value

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class application_parameters
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
class application_parameters:
    def __init__(self, argv):
        self.no_effect = False
        self.no_sound = False
        self.fullscreen = False
        self.use_mouse = False
        self.use_gpio = False
        self.rotate_txt = False
        self.show_fps = False
        if len(sys.argv) > 1:
            for i in range(1, len(argv)):
                if "--no-effect" in argv[i]:
                    logging.info("argument : no-effect")
                    self.no_effect = True
                elif "--no-sound" in argv[i]:
                    logging.info("argument : no-sound")
                    self.no_sound = True
                elif "--use-mouse" in argv[i]:
                    logging.info("argument : use-mouse")
                    self.use_mouse = True
                elif "--use-gpio" in argv[i]:
                    logging.info("argument : use-gpio")
                    self.use_gpio = True
                elif "--rotate-txt" in argv[i]:
                    logging.info("argument : rotate-txt")
                    self.rotate_txt = True
                elif "--help-gpio" in argv[i]:
                    logging.info("argument : help-gpio")
                    help_gpio()
                    sys.exit()
                elif "--show-fps" in argv[i]:
                    logging.info("argument : show-fps")
                    self.show_fps = True
                elif "--fullscreen" in argv[i]:
                    logging.info("argument : fullscreen")
                    self.fullscreen = True
                else:
                    help()
                    sys.exit()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class font
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
class font:
    def __init__(self, responsive):
        bundle_font_dir = getattr(sys, '_MEIPASS', "font") # Check if MEIPASS attribute is available in sys else return current file path
        path_to_font = os.path.abspath(os.path.join(bundle_font_dir,'SevenSegment.ttf'))
        self.font_large = pygame.font.Font(path_to_font, responsive.FONT_LARGE_SIZE)
        self.font_small = pygame.font.Font(path_to_font, responsive.FONT_SMALL_SIZE)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class sfx
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
class sfx:
    def __init__(self):
        pygame.mixer.set_num_channels(3)
        bundle_sound_dir = getattr(sys, '_MEIPASS', "sfx") # Check if MEIPASS attribute is available in sys else return current file path
        self.paddle_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'paddle.wav')))
        self.wall_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'wall.wav')))
        self.score_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'score.wav')))
        self.start_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'start.wav')))
        self.gameover_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'gameover.wav')))
        self.laser_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'laser.wav')))
        self.explosion_sound = pygame.mixer.Sound(os.path.abspath(os.path.join(bundle_sound_dir,'explosion.wav')))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class Dust_particle
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class Dust
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class Firework_particle
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class Firework
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class Flame_particle
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class Flame
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
class Flame:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.flame_intensity = 2
        self.flame_particles = []
        for i in range(self.flame_intensity * 25):
            self.flame_particles.append(Flame_particle(self.x + random.randint(-5, 5), self.y, random.randint(1, 5)))


    def update_flame(self):
        for i in self.flame_particles:
            if i.original_r <= 0:
                self.flame_particles.remove(i)
                self.flame_particles.append(Flame_particle(self.x + random.randint(-5, 5), self.y, random.randint(1, 5)))
                del i
                continue
            i.update()

    def draw_flame(self, surface, color):
        for i in self.flame_particles:
            i.draw(surface, color)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class Shiny_particle
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
class Shiny_particle:
    alpha_layer_qty = 2
    alpha_glow_difference_constant = 2

    def __init__(self, x, y, r=5):
        self.x = x
        self.y = y
        self.r = r
        self.original_r = r
        self.alpha_layers = Shiny_particle.alpha_layer_qty
        self.alpha_glow = Shiny_particle.alpha_glow_difference_constant
        max_surf_size = 2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        self.surf = pygame.Surface((max_surf_size, max_surf_size), pygame.SRCALPHA)
        self.burn_rate = 0.1 * random.randint(1, 4)

    def update(self):
        #self.y -= 7 - self.r
        #self.x += random.randint(-self.r, self.r)
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
            r, g, b = color
            color_alpha = (r, g, b, alpha)
            pygame.draw.circle(self.surf, color_alpha, (self.surf.get_width() // 2, self.surf.get_height() // 2), radius)
        surface.blit(self.surf, self.surf.get_rect(center=(self.x, self.y)))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class Shiny
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
class Shiny:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shiny_intensity = 2
        self.shiny_particles = []
        for i in range(self.shiny_intensity * 25):
            self.shiny_particles.append(Shiny_particle(self.x, self.y, random.randint(1, 5)))


    def update_shiny(self):
        for i in self.shiny_particles:
            if i.original_r <= 0:
                self.shiny_particles.remove(i)
                self.shiny_particles.append(Shiny_particle(self.x, self.y, random.randint(1, 5)))
                del i
                continue
            i.update()

    def draw_shiny(self, surface, color):
        for i in self.shiny_particles:
            i.draw(surface, color)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Class Halo_frame
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
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

    def draw(self, surface, color):
        pygame.draw.line(surface, color, (0,0), (surface.get_width(),0), self.line_width)
        pygame.draw.line(surface, color, (surface.get_width(),0), (surface.get_width(),surface.get_height()), self.line_width)
        pygame.draw.line(surface, color, (surface.get_width(),surface.get_height()), (0,surface.get_height()), self.line_width)
        pygame.draw.line(surface, color, (0,surface.get_height()), (0,0), self.line_width)

# ############################################################################################################################################################
# Fonctions
# ############################################################################################################################################################

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction d'aide
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction d'aide sur le connecteur GPIO
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
def help_gpio():
    print(f"""
        **********************************************************************************
        *                          {Fore.CYAN}RASPBERRY Pi GPIO Connector{Style.RESET_ALL}                           *
        **********************************************************************************
        *                                                                                *
        *                                   Pin 1 Pin2                                   *
        *                                {Fore.MAGENTA}+3V3{Style.RESET_ALL} [ ] [ ] {Fore.RED}+5V{Style.RESET_ALL}                                *
        *                      SDA1 / {Fore.GREEN}GPIO  2{Style.RESET_ALL} [ ] [ ] {Fore.RED}+5V{Style.RESET_ALL}                                *
        *                      SCL1 / {Fore.GREEN}GPIO  3{Style.RESET_ALL} [ ] [ ] {Style.DIM}GND{Style.RESET_ALL}                                *
        *                             {Fore.GREEN}GPIO  4{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 14{Style.RESET_ALL} / TXD0                     *
        *                                 {Style.DIM}GND{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 15{Style.RESET_ALL} / RXD0                     *
        *                             {Fore.GREEN}GPIO 17{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 18{Style.RESET_ALL}                            *
        *                             {Fore.GREEN}GPIO 27{Style.RESET_ALL} [ ] [ ] {Style.DIM}GND{Style.RESET_ALL} -----------------[SWITCH LEFT] *
        *                             {Fore.GREEN}GPIO 22{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 23{Style.RESET_ALL} -------------[SWITCH LEFT] *
        *                                {Fore.MAGENTA}+3V3{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 24{Style.RESET_ALL}                            *
        *                      MOSI / {Fore.GREEN}GPIO 10{Style.RESET_ALL} [ ] [ ] {Style.DIM}GND{Style.RESET_ALL} ----------------[SWITCH RIGHT] *
        *                      MISO / {Fore.GREEN}GPIO  9{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 25{Style.RESET_ALL} ------------[SWITCH RIGHT] *
        *                      SCLK / {Fore.GREEN}GPIO 11{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO  8{Style.RESET_ALL} / CE0#                     *
        *                                 {Style.DIM}GND{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO  7{Style.RESET_ALL} / CE1#                     *
        *                     ID_SD / {Fore.GREEN}GPIO  0{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO  1{Style.RESET_ALL} / ID_SC                    *
        *                             {Fore.GREEN}GPIO  5{Style.RESET_ALL} [ ] [ ] {Style.DIM}GND{Style.RESET_ALL} ----------------[SWITCH RESET] *
        *                             {Fore.GREEN}GPIO  6{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 12{Style.RESET_ALL} ------------[SWITCH RESET] *
        *                             {Fore.GREEN}GPIO 13{Style.RESET_ALL} [ ] [ ] {Style.DIM}GND{Style.RESET_ALL}                                *
        *                      MISO / {Fore.GREEN}GPIO 19{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 16{Style.RESET_ALL} / CE2#                     *
        *                             {Fore.GREEN}GPIO 26{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 20{Style.RESET_ALL} / MOSI                     *
        *                                 {Style.DIM}GND{Style.RESET_ALL} [ ] [ ] {Fore.GREEN}GPIO 21{Style.RESET_ALL} / SCLK                     *
        *                                  Pin 39 Pin 40                                 *
        *                                                                                *
        **********************************************************************************

    """)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction d'initialisation des interface GPIO
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# def rotation_decode(channel):
#     global rotation_counter_left
#     global rotation_counter_right

#     Switch_Left_A = GPIO.input(GPIO_ROTARY_LEFT_A)
#     Switch_Left_B = GPIO.input(GPIO_ROTARY_LEFT_B)

#     logging.info('--------------------------------')
#     logging.info('Switch_Left_A %s' % Switch_Left_A)
#     logging.info('Switch_Left_B %s' % Switch_Left_B)

#     if (Switch_Left_A == 1) and (Switch_Left_B == 0):
#         rotation_counter_left += 1
#         event_actions.append("LEFT_PADDLE_UP")
#         logging.info('direction -> %s' % rotation_counter_left)
#         while Switch_Left_B == 0:
#             Switch_Left_B = GPIO.input(GPIO_ROTARY_LEFT_B)
#         while Switch_Left_B == 1:
#             Switch_Left_B = GPIO.input(GPIO_ROTARY_LEFT_B)
#         return

#     elif (Switch_Left_A == 1) and (Switch_Left_B == 1):
#         rotation_counter_left -= 1
#         event_actions.append("LEFT_PADDLE_DOWN")
#         logging.info('direction <- %s' % rotation_counter_left)
#         while Switch_Left_A == 1:
#             Switch_Left_A = GPIO.input(GPIO_ROTARY_LEFT_A)
#         return
#     else:
#         return

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction d'initialisation des interface GPIO
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
def init_GPIO():
    logging.info("Rotary Encoder Test Program")
    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM)
    #GPIO.setup(GPIO_ROTARY_LEFT_A, GPIO.IN)
    #GPIO.setup(GPIO_ROTARY_LEFT_B, GPIO.IN)
    #GPIO.add_event_detect(GPIO_ROTARY_LEFT_A, GPIO.BOTH, rotation_decode, GPIO_BOUNCE_TIME)
    #GPIO.add_event_detect(GPIO_ROTARY_LEFT_A, GPIO.BOTH, rotation_decode)
    # GPIO.add_event_detect(GPIO_ROTARY_LEFT_A, GPIO.BOTH)
    # GPIO.add_event_callback(GPIO_ROTARY_LEFT_A, rotation_decode)
    #– BOTH, déclenche l’interrupt quand le pin change d’état ( de bas à haut , ou de haut à bas )
    #– RISING, sur front montant, il se déclenche seulement quand on va passer d’un état bas à haut
    #– FALLING, sur front descendant, il se déclenche seulement quand on va passer d’un état haut à bas
    GPIO.setup(GPIO_BUTTON_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(GPIO_BUTTON_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(GPIO_BUTTON_RESET, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction pour dessiner les raquettes
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
def draw_paddles(surface, color, left_paddle_y, right_paddle_y, paddle_with, paddle_height, line_width):
    pygame.draw.rect(surface, color, (int(line_width), int(left_paddle_y - paddle_height / 2) , paddle_with, paddle_height))
    pygame.draw.rect(surface, color, (int(surface.get_width() - paddle_with - line_width), int(right_paddle_y - paddle_height / 2), paddle_with, paddle_height))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction pour dessiner la balle
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
def draw_ball(surface, color, ball_x, ball_y, size):
    pygame.draw.rect(surface, color, (int(ball_x-size/2), int(ball_y-size/2), int(size), int(size)))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction pour afficher le FPS
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
def draw_fps(surface, color, font, text):
        text = font.render(text, True, color)
        surface.blit(text, (10, 10))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction pour afficher le score
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction pour afficher le texte de fin de jeu
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction pour afficher une ligne en pointilles
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction pour afficher la cadre de jeu
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
def draw_frame(surface, color, width=1):
    pygame.draw.line(surface, color, (0,0), (surface.get_width(),0), width)
    pygame.draw.line(surface, color, (surface.get_width(),0), (surface.get_width(),surface.get_height()), width)
    pygame.draw.line(surface, color, (surface.get_width(),surface.get_height()), (0,surface.get_height()), width)
    pygame.draw.line(surface, color, (0,surface.get_height()), (0,0), width)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fonction de boucle
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
def pygame_event_loop(loop, event_queue):

    logging.info("init event loop")

    while True:
        event = pygame.event.wait()
        asyncio.run_coroutine_threadsafe(event_queue.put(event), loop=loop)

# ############################################################################################################################################################
# Fonction asynchrone de gestion des animations
# ############################################################################################################################################################
async def animation(surface, app_param, app_values, font, responsive, sfx):

    logging.info("init animation")

    current_time = 0
    last_time = 0
    last_move_left = 0
    last_move_right = 0
    last_time_effect = 0
    last_time_fps = 0
    last_fps = current_fps = 0
    count_fps = 1
    while True:
        last_time, current_time = current_time, time.time()
        await asyncio.sleep(1 / MAX_FPS - (current_time - last_time))  # tick

        if app_values.game_paused == False:

            # déplacement de la raquette gauche
            if app_values.left_paddle_move == "MOUSE_UP":
                decelerate = ((current_time - last_move_left) * PADDLE_DECELERATE_MOUSE)
                app_values.left_paddle_y -=  responsive.PADDLE_SPEED_MOUSE / (decelerate if decelerate > 1 else 1)
                app_values.left_paddle_move = "NONE"
                last_move_left = current_time
            elif app_values.left_paddle_move == "MOUSE_DOWN":
                decelerate = ((current_time - last_move_left) * PADDLE_DECELERATE_MOUSE)
                app_values.left_paddle_y +=  responsive.PADDLE_SPEED_MOUSE / (decelerate if decelerate > 1 else 1)
                app_values.left_paddle_move = "NONE"
                last_move_left = current_time
            elif app_values.left_paddle_move == "KEYBOARD_UP":
                app_values.left_paddle_y -= (current_time - last_time) * responsive.PADDLE_SPEED_KEYBOARD
            elif app_values.left_paddle_move == "KEYBOARD_DOWN":
                app_values.left_paddle_y +=  (current_time - last_time) * responsive.PADDLE_SPEED_KEYBOARD

            # Limites de déplacement de la raquette gauche
            if app_values.left_paddle_y < LINE_WIDTH + responsive.PADDLE_HEIGHT / 2:
                app_values.left_paddle_y = LINE_WIDTH + responsive.PADDLE_HEIGHT / 2
            if app_values.left_paddle_y > surface.get_height() - LINE_WIDTH - responsive.PADDLE_HEIGHT / 2:
                app_values.left_paddle_y = surface.get_height() - LINE_WIDTH - responsive.PADDLE_HEIGHT / 2

            # déplacement de la raquette droite
            if app_values.right_paddle_move == "MOUSE_UP":
                decelerate = ((current_time - last_move_right) * PADDLE_DECELERATE_MOUSE)
                app_values.right_paddle_y -= responsive.PADDLE_SPEED_MOUSE / (decelerate if decelerate > 1 else 1)
                app_values.right_paddle_move = "NONE"
                last_move_right = current_time
            elif app_values.right_paddle_move == "MOUSE_DOWN":
                decelerate = ((current_time - last_move_right) * PADDLE_DECELERATE_MOUSE)
                app_values.right_paddle_y += responsive.PADDLE_SPEED_MOUSE / (decelerate if decelerate > 1 else 1)
                app_values.right_paddle_move = "NONE"
                last_move_right = current_time
            elif app_values.right_paddle_move == "KEYBOARD_UP":
                app_values.right_paddle_y -=  (current_time - last_time) * responsive.PADDLE_SPEED_KEYBOARD
            elif app_values.right_paddle_move == "KEYBOARD_DOWN":
                app_values.right_paddle_y +=  (current_time - last_time) * responsive.PADDLE_SPEED_KEYBOARD

            # Limites de déplacement de la raquette droite
            if app_values.right_paddle_y < LINE_WIDTH + responsive.PADDLE_HEIGHT / 2:
                app_values.right_paddle_y = LINE_WIDTH + responsive.PADDLE_HEIGHT / 2
            if app_values.right_paddle_y > surface.get_height() - LINE_WIDTH - responsive.PADDLE_HEIGHT / 2:
                app_values.right_paddle_y = surface.get_height() - LINE_WIDTH - responsive.PADDLE_HEIGHT / 2

        if app_values.game_started == True:

            # déplacement de la balle
            app_values.ball_x += (current_time - last_time) * app_values.ball_speed_x
            app_values.ball_y += (current_time - last_time) * app_values.ball_speed_y

            # rebond de la balle sur le haut
            if app_values.ball_y <= responsive.BALL_SIZE/2:
                if not app_param.no_sound: pygame.mixer.Channel(2).play(sfx.wall_sound)
                app_values.ball_y = responsive.BALL_SIZE/2
                app_values.ball_speed_y = -app_values.ball_speed_y
                if not app_param.no_effect: dust_effects.append(Dust(app_values.ball_x, app_values.ball_y - responsive.BALL_SIZE/2, app_values.main_color, DIRECTION_DOWN))

            # rebond de la balle sur la bas
            if app_values.ball_y >= surface.get_height() - responsive.BALL_SIZE/2:
                if not app_param.no_sound: pygame.mixer.Channel(2).play(sfx.wall_sound)
                app_values.ball_y = surface.get_height() - responsive.BALL_SIZE/2
                app_values.ball_speed_y = -app_values.ball_speed_y
                if not app_param.no_effect: dust_effects.append(Dust(app_values.ball_x, app_values.ball_y + responsive.BALL_SIZE/2, app_values.main_color, DIRECTION_UP))

            # rebond de la balle sur la raquette gauche
            if app_values.ball_x <= LINE_WIDTH + SPACE_WIDTH + responsive.PADDLE_WIDTH + responsive.BALL_SIZE / 2 and app_values.left_paddle_y - responsive.PADDLE_HEIGHT / 2 - responsive.BALL_SIZE / 2 < app_values.ball_y < app_values.left_paddle_y + responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2 :
                if not app_param.no_sound: pygame.mixer.Channel(1).play(sfx.paddle_sound)
                app_values.ball_speed += BALL_ACCELERATION * (1 if app_values.ball_speed > 0 else -1)  # Augmentation de la vitesse
                app_values.ball_speed = max(min(app_values.ball_speed, responsive.BALL_MAX_SPEED), -responsive.BALL_MAX_SPEED) # Vitesse maximale
                if abs(app_values.ball_speed) >= responsive.BALL_MAX_SPEED and app_values.ball_in_fire == False:
                    if not app_param.no_effect: shiny_effects.append(Shiny(app_values.ball_x, app_values.ball_y))
                    app_values.ball_in_fire = True
                app_values.ball_speed_x = -app_values.ball_speed_x
                app_values.ball_x = LINE_WIDTH + SPACE_WIDTH + responsive.PADDLE_WIDTH + responsive.BALL_SIZE / 2
                if not app_param.no_effect: dust_effects.append(Dust(app_values.ball_x - responsive.BALL_SIZE / 2, app_values.ball_y, app_values.main_color, DIRECTION_RIGHT))
                # Calcul de l'angle de rebond base sur la position relative de la balle sur la raquette
                relative_intersect_y = app_values.left_paddle_y - app_values.ball_y
                normalized_intersect_y = relative_intersect_y / (responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2)
                bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degres)
                app_values.ball_speed_x = app_values.ball_speed * math.cos(bounce_angle)
                app_values.ball_speed_y = app_values.ball_speed * -math.sin(bounce_angle)

            # rebond de la balle sur la raquette droite
            if app_values.ball_x >= surface.get_width() - LINE_WIDTH - SPACE_WIDTH - responsive.PADDLE_WIDTH - responsive.BALL_SIZE / 2 and app_values.right_paddle_y  - responsive.PADDLE_HEIGHT / 2 - responsive.BALL_SIZE / 2 < app_values.ball_y < app_values.right_paddle_y + responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2:
                if not app_param.no_sound: pygame.mixer.Channel(1).play(sfx.paddle_sound)
                app_values.ball_speed += BALL_ACCELERATION * (1 if app_values.ball_speed > 0 else -1)  # Augmentation de la vitesse
                app_values.ball_speed = max(min(app_values.ball_speed, responsive.BALL_MAX_SPEED), -responsive.BALL_MAX_SPEED) # Vitesse maximale
                if abs(app_values.ball_speed) >= responsive.BALL_MAX_SPEED and app_values.ball_in_fire == False:
                    if not app_param.no_effect: shiny_effects.append(Shiny(app_values.ball_x, app_values.ball_y))
                    app_values.ball_in_fire = True
                app_values.ball_speed_x = -app_values.ball_speed_x
                app_values.ball_x = surface.get_width() - LINE_WIDTH - SPACE_WIDTH - responsive.PADDLE_WIDTH - responsive.BALL_SIZE / 2
                if not app_param.no_effect: dust_effects.append(Dust(app_values.ball_x + responsive.BALL_SIZE / 2, app_values.ball_y, app_values.main_color, DIRECTION_LEFT))
                # Calcul de l'angle de rebond base sur la position relative de la balle sur la raquette
                relative_intersect_y = app_values.right_paddle_y - app_values.ball_y
                normalized_intersect_y = relative_intersect_y / (responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2)
                bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degres)
                app_values.ball_speed_x = -app_values.ball_speed * math.cos(bounce_angle)
                app_values.ball_speed_y = app_values.ball_speed * -math.sin(bounce_angle)

            # Sortie de la balle a gauche
            if app_values.ball_x <= LINE_WIDTH + SPACE_WIDTH + responsive.BALL_SIZE / 2:
                app_values.right_score += 1
                if app_values.right_score < WIN_SCORE:
                    if not app_param.no_sound: pygame.mixer.Channel(0).play(sfx.score_sound)
                else:
                    if not app_param.no_sound: pygame.mixer.Channel(0).play(sfx.gameover_sound)
                app_values.registered_ball_x_position = app_values.ball_x
                app_values.registered_ball_y_position = app_values.ball_y
                app_values.ball_speed_x = 0
                app_values.ball_speed_y = 0
                app_values.game_started = False
                app_values.game_paused = True
                app_values.ball_replace_timer = time.time()
                app_values.current_player = 1
                if not app_param.no_effect: Halo_frame_effects.append(Halo_frame(HALO_FRAME_WIDTH, HALO_FRAME_COUNT, HALO_FRAME_SPEED))
                if app_values.right_score >= WIN_SCORE:
                    app_values.ball_speed = responsive.BALL_INIT_SPEED
                    app_values.ball_in_fire = False
                    app_values.game_started = False

            # Sortie de la balle a droite
            if app_values.ball_x >= surface.get_width() - LINE_WIDTH - SPACE_WIDTH - responsive.BALL_SIZE / 2:
                app_values.left_score += 1
                if app_values.left_score < WIN_SCORE:
                    if not app_param.no_sound: pygame.mixer.Channel(0).play(sfx.score_sound)
                else:
                    if not app_param.no_sound: pygame.mixer.Channel(0).play(sfx.gameover_sound)
                app_values.registered_ball_x_position = app_values.ball_x
                app_values.registered_ball_y_position = app_values.ball_y
                app_values.ball_speed_x = 0
                app_values.ball_speed_y = 0
                app_values.game_started = False
                app_values.game_paused = True
                app_values.ball_replace_timer = time.time()
                app_values.current_player = 2
                if not app_param.no_effect: Halo_frame_effects.append(Halo_frame(HALO_FRAME_WIDTH, HALO_FRAME_COUNT, HALO_FRAME_SPEED))
                if app_values.left_score >= WIN_SCORE:
                    app_values.ball_speed = responsive.BALL_INIT_SPEED
                    app_values.ball_in_fire = False
                    app_values.game_started = False

        else:

            if app_values.game_paused == False:

                # Suivi de la balle sur la raquette
                app_values.ball_speed_x = 0
                app_values.ball_speed_y = 0
                if ( app_values.current_player == 1 ):
                    app_values.ball_x = responsive.PADDLE_WIDTH + SPACE_WIDTH + responsive.BALL_SIZE / 2 + LINE_WIDTH
                    if abs(app_values.ball_y - app_values.left_paddle_y) < responsive.BALL_INERTIA: app_values.ball_y = app_values.left_paddle_y
                    if app_values.ball_y < app_values.left_paddle_y: app_values.ball_y += responsive.BALL_INERTIA
                    if app_values.ball_y > app_values.left_paddle_y: app_values.ball_y -= responsive.BALL_INERTIA
                    if app_values.ball_y < app_values.left_paddle_y - responsive.PADDLE_HEIGHT / 2: app_values.ball_y = app_values.left_paddle_y - responsive.PADDLE_HEIGHT / 2
                    if app_values.ball_y > app_values.left_paddle_y + responsive.PADDLE_HEIGHT / 2: app_values.ball_y = app_values.left_paddle_y + responsive.PADDLE_HEIGHT / 2
                elif ( app_values.current_player == 2 ):
                    app_values.ball_x = surface.get_width() - responsive.PADDLE_WIDTH - SPACE_WIDTH - responsive.BALL_SIZE / 2 - LINE_WIDTH
                    if abs(app_values.ball_y - app_values.right_paddle_y) < responsive.BALL_INERTIA: app_values.ball_y = app_values.right_paddle_y
                    if app_values.ball_y < app_values.right_paddle_y: app_values.ball_y += responsive.BALL_INERTIA
                    if app_values.ball_y > app_values.right_paddle_y: app_values.ball_y -= responsive.BALL_INERTIA
                    if app_values.ball_y < app_values.right_paddle_y - responsive.PADDLE_HEIGHT / 2: app_values.ball_y = app_values.right_paddle_y - responsive.PADDLE_HEIGHT / 2
                    if app_values.ball_y > app_values.right_paddle_y + responsive.PADDLE_HEIGHT / 2: app_values.ball_y = app_values.right_paddle_y + responsive.PADDLE_HEIGHT / 2

        # Replacement de la balle
        if app_values.game_paused == True:
            progress = (time.time() - app_values.ball_replace_timer) * 1000 / BALL_REPLACE_DURATION
            if progress <= 1:
                if app_values.current_player == 1:
                    app_values.ball_x = app_values.registered_ball_x_position - ((app_values.registered_ball_x_position - (responsive.PADDLE_WIDTH + SPACE_WIDTH + responsive.BALL_SIZE / 2 + LINE_WIDTH)) * progress)
                    app_values.ball_y = app_values.registered_ball_y_position - ((app_values.registered_ball_y_position - app_values.left_paddle_y) * progress)
                if app_values.current_player == 2:
                    app_values.ball_x = app_values.registered_ball_x_position - ((app_values.registered_ball_x_position - (surface.get_width() - responsive.PADDLE_WIDTH - SPACE_WIDTH - responsive.BALL_SIZE / 2 - LINE_WIDTH)) * progress)
                    app_values.ball_y = app_values.registered_ball_y_position - ((app_values.registered_ball_y_position - app_values.right_paddle_y) * progress)
            else:
                # Reprise du jeu
                app_values.game_paused = False

        surface.fill(BLACK)

        # Mise a jour des effets de particules
        if 1/(current_time - last_time_effect) <= EFFECT_FPS:

            last_time_effect = current_time

            for particle in dust_effects:
                if len(particle.particles) > 0:
                    particle.update()
                else:
                    dust_effects.remove(particle)
                    del particle

            for firework in firework_effects:
                if len(firework.particles) > 0 or firework.exploded == False:
                    firework.move(surface, app_param.no_sound, sfx.explosion_sound)
                else:
                    firework_effects.remove(firework)
                    del firework

            for shiny in shiny_effects:
                if app_values.ball_speed >= responsive.BALL_MAX_SPEED:
                    shiny.x = app_values.ball_x
                    shiny.y = app_values.ball_y
                    shiny.update_shiny()
                else:
                    shiny_effects.remove(shiny)
                    del shiny

            for halo in Halo_frame_effects:
                if halo.count > 0:
                    halo.move()
                else:
                    Halo_frame_effects.remove(halo)
                    del halo

        # Affichage des effets de particules
        for particle in dust_effects:
            if len(particle.particles) > 0:
                particle.draw(surface)
        for firework in firework_effects:
            if len(firework.particles) > 0 or firework.exploded == False:
                firework.draw(surface)
        for shiny in shiny_effects:
            if app_values.ball_speed >= responsive.BALL_MAX_SPEED:
                shiny.draw_shiny(surface, app_values.main_color)
        for halo in Halo_frame_effects:
            if halo.count > 0:
                halo.draw(surface, app_values.main_color)

        # Calcul du FPS moyen
        if app_param.show_fps:
            if (current_time - last_time_fps) > 0.5:
                last_time_fps = current_time
                last_fps = int(current_fps / count_fps)
                current_fps = int(1/(current_time - last_time))
                count_fps = 1
            else:
                current_fps += int(1/(current_time - last_time))
                count_fps += 1

        draw_frame(surface, app_values.main_color, LINE_WIDTH)
        draw_dashed_line(surface, app_values.main_color, (surface.get_width() / 2, 0), (surface.get_width() / 2, surface.get_height()), LINE_WIDTH, responsive.DASH_LENGTH)
        draw_paddles(surface, app_values.main_color, app_values.left_paddle_y, app_values.right_paddle_y, responsive.PADDLE_WIDTH, responsive.PADDLE_HEIGHT, LINE_WIDTH)
        draw_ball(surface, app_values.main_color, app_values.ball_x, app_values.ball_y, responsive.BALL_SIZE)
        draw_score(surface, app_values.main_color, font.font_large, responsive.FONT_LARGE_SIZE, app_param.rotate_txt, app_values.left_score, app_values.right_score)
        draw_endgame(surface, app_values.main_color, font.font_large, responsive.FONT_LARGE_SIZE, app_param.rotate_txt, app_values.left_score, app_values.right_score)
        if app_param.show_fps: draw_fps(surface, app_values.main_color, font.font_small, str(last_fps))

        pygame.display.flip()

# ############################################################################################################################################################
# Fonction asynchrone de détection des evenements
# ############################################################################################################################################################
async def handle_events(event_queue, surface, app_param, app_values, responsive, sfx):

    logging.info("init handle events")

    while True:

        # ==================================================================================================
        # Catch event
        event = await event_queue.get()

        #print("event", event)

        if event.type == pygame.QUIT:
            event_actions.append("EXIT")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                event_actions.append("EXIT")
            if event.key == pygame.K_r:
                event_actions.append("RESET")
            if event.key == pygame.K_LCTRL:
                if app_values.game_paused == False:
                    event_actions.append("LEFT_PADDLE_BUTTON")
            if event.key == pygame.K_RCTRL:
                if app_values.game_paused == False:
                    event_actions.append("RIGHT_PADDLE_BUTTON")
            if event.key == pygame.K_w or event.key == pygame.K_z:
                app_values.left_paddle_move = "KEYBOARD_UP"
            if event.key == pygame.K_s:
                app_values.left_paddle_move = "KEYBOARD_DOWN"
            if event.key == pygame.K_UP:
                app_values.right_paddle_move = "KEYBOARD_UP"
            if event.key == pygame.K_DOWN:
                app_values.right_paddle_move = "KEYBOARD_DOWN"

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_z:
                if app_values.left_paddle_move == "KEYBOARD_UP": app_values.left_paddle_move = "NONE"
            if event.key == pygame.K_s:
                if app_values.left_paddle_move == "KEYBOARD_DOWN": app_values.left_paddle_move = "NONE"
            if event.key == pygame.K_UP:
                if app_values.right_paddle_move == "KEYBOARD_UP": app_values.right_paddle_move = "NONE"
            if event.key == pygame.K_DOWN:
                if app_values.right_paddle_move == "KEYBOARD_DOWN": app_values.right_paddle_move = "NONE"

        if event.type == pygame.MOUSEBUTTONDOWN and app_param.use_mouse == True:
            # Barre gauche - click gauche
            if event.button == 1:
                event_actions.append("LEFT_PADDLE_BUTTON")
            # click central
            elif event.button == 2:
                event_actions.append("RESET")
            # Barre droite - click droite
            elif event.button == 3:
                event_actions.append("RIGHT_PADDLE_BUTTON")

        if event.type == pygame.MOUSEMOTION and app_param.use_mouse == True:
            # Recuperation de la position du curseur
            rel_x, rel_y = event.rel
            # Barre gauche - mouvement horizontal
            if rel_x < 0:
                app_values.left_paddle_move = "MOUSE_UP"
            elif rel_x > 0:
                app_values.left_paddle_move = "MOUSE_DOWN"
            # Barre droite - mouvement vetical
            if rel_y < 0:
                app_values.right_paddle_move = "MOUSE_UP"
            elif rel_y > 0:
                app_values.right_paddle_move = "MOUSE_DOWN"

        if event.type == GPIO_BUTTON_LEFT_EVENT:
                event_actions.append("LEFT_PADDLE_BUTTON")

        if event.type == GPIO_BUTTON_RIGHT_EVENT:
                event_actions.append("RIGHT_PADDLE_BUTTON")

        if event.type == GPIO_BUTTON_RESET_EVENT:
                event_actions.append("RESET")

        # ==================================================================================================
        # Process event
        for action in event_actions:
            #print(action)
            if action == "LEFT_PADDLE_BUTTON":
                if not app_values.game_started and not app_values.game_paused:
                    # re-initialisation des scores
                    if app_values.right_score >= WIN_SCORE:
                        app_values.right_score = 0
                        app_values.left_score = 0
                    # Lancement de la balle a droite
                    if ( app_values.current_player == 1 ):
                        if not app_param.no_effect: dust_effects.append(Dust(app_values.ball_x-responsive.BALL_SIZE / 2, app_values.ball_y, app_values.main_color, DIRECTION_RIGHT))
                        # Calcul de l'angle de rebond base sur la position relative de la balle sur la raquette
                        relative_intersect_y = app_values.left_paddle_y - app_values.ball_y
                        normalized_intersect_y = relative_intersect_y / (responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2)
                        bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degres)
                        app_values.ball_speed_x = app_values.ball_speed * math.cos(bounce_angle)
                        app_values.ball_speed_y = app_values.ball_speed * -math.sin(bounce_angle)
                        app_values.game_started = True
                    # Feu d'atifice
                    if ( app_values.current_player == 2  and app_values.left_score >= WIN_SCORE ):
                        if not app_param.no_effect:
                            if not app_param.no_sound: pygame.mixer.Channel(1).play(sfx.laser_sound)
                            firework_color = random.choice(FIREWORK_COLORS)
                            firework_effects.append(Firework(responsive.PADDLE_WIDTH + SPACE_WIDTH, app_values.left_paddle_y, firework_color, DIRECTION_RIGHT))
                            dust_effects.append(Dust(responsive.PADDLE_WIDTH + SPACE_WIDTH, app_values.left_paddle_y, firework_color, DIRECTION_RIGHT))
            # --------------------------------------------------------------------------------------------------
            elif action == "RIGHT_PADDLE_BUTTON":
                if not app_values.game_started and not app_values.game_paused:
                    # re-initialisation des scores
                    if app_values.left_score >= WIN_SCORE:
                        app_values.right_score = 0
                        app_values.left_score = 0
                    # Lancement de la balle a gauche
                    if ( app_values.current_player == 2 ):
                        if not app_param.no_effect: dust_effects.append(Dust(app_values.ball_x+responsive.BALL_SIZE / 2, app_values.ball_y, app_values.main_color, DIRECTION_LEFT))
                        # Calcul de l'angle de rebond base sur la position relative de la balle sur la raquette
                        relative_intersect_y = app_values.right_paddle_y - app_values.ball_y
                        normalized_intersect_y = relative_intersect_y / (responsive.PADDLE_HEIGHT / 2 + responsive.BALL_SIZE / 2)
                        bounce_angle = normalized_intersect_y * (math.pi / 4)  # Angle de rebond maximal de pi/4 radians (45 degres)
                        app_values.ball_speed_x = -app_values.ball_speed * math.cos(bounce_angle)
                        app_values.ball_speed_y = app_values.ball_speed * -math.sin(bounce_angle)
                        app_values.game_started = True
                    # Feu d'atifice
                    if ( app_values.current_player == 1 and app_values.right_score >= WIN_SCORE):
                        if not app_param.no_effect:
                            if not app_param.no_sound: pygame.mixer.Channel(1).play(sfx.laser_sound)
                            firework_color = random.choice(FIREWORK_COLORS)
                            firework_effects.append(Firework(surface.get_width() - responsive.PADDLE_WIDTH - SPACE_WIDTH, app_values.right_paddle_y, firework_color, DIRECTION_LEFT))
                            dust_effects.append(Dust(surface.get_width() - responsive.PADDLE_WIDTH - SPACE_WIDTH, app_values.right_paddle_y, firework_color, DIRECTION_LEFT))
            # --------------------------------------------------------------------------------------------------
            elif action == "RESET":
                app_values.right_score = 0
                app_values.left_score = 0
                app_values.ball_speed = responsive.BALL_INIT_SPEED
                app_values.ball_in_fire = False
            # --------------------------------------------------------------------------------------------------
            elif action == "EXIT":
                pygame.QUIT
                asyncio.get_event_loop().stop()
            # --------------------------------------------------------------------------------------------------
            event_actions.remove(action) # Purge de l'action

# ############################################################################################################################################################
# Fonction asynchrone de détection des evenements GPIO
# ############################################################################################################################################################
async def handle_gpio(event_queue, surface, app_param, app_values, responsive, sfx):

    logging.info("init GPIO events")
    previous_button_left = GPIO.HIGH
    previous_button_right = GPIO.HIGH
    previous_button_reset = GPIO.HIGH

    while True:
        # Lecture de l'état du bouton
        button_left = GPIO.input(GPIO_BUTTON_LEFT)
        button_right = GPIO.input(GPIO_BUTTON_RIGHT)
        button_reset = GPIO.input(GPIO_BUTTON_RESET)

        if button_left == GPIO.LOW and previous_button_left == GPIO.HIGH:
            if app_values.game_paused == False:
                pygame.event.post(pygame.event.Event(GPIO_BUTTON_LEFT_EVENT))

        if button_right == GPIO.LOW and previous_button_right == GPIO.HIGH:
            if app_values.game_paused == False:
                pygame.event.post(pygame.event.Event(GPIO_BUTTON_RIGHT_EVENT))

        if button_reset == GPIO.LOW and previous_button_reset == GPIO.HIGH:
            if app_values.game_paused == False:
                pygame.event.post(pygame.event.Event(GPIO_BUTTON_RESET_EVENT))

        # Enregistrement de l'état des boutons
        previous_button_left = button_left
        previous_button_right = button_right
        previous_button_reset = button_reset

        await asyncio.sleep(0.1)

# ############################################################################################################################################################
# Fonction principale
# ############################################################################################################################################################

def main():

    loop = asyncio.get_event_loop()
    event_queue = asyncio.Queue()

    # Controle des parametres d'entree
    app_param = application_parameters(sys.argv)

    # pygame.key.set_repeat(20)

    # Definition du mode d'affichage
    if app_param.fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong")
        bundle_image_dir = getattr(sys, '_MEIPASS', "image") # Check if MEIPASS attribute is available in sys else return current file path
        icon = pygame.image.load(os.path.abspath(os.path.join(bundle_image_dir,'logo.png'))).convert_alpha()
        pygame.display.set_icon(icon)

    # Initialisation des interface GPIO
    if app_param.use_gpio:
        if _rpi_gpio_Loaded:
            init_GPIO()
        else:
            logging.warning("no GPIO found")

    # Chargement des effets sonores
    sfx_lib = None
    if not app_param.no_sound:
        sfx_lib = sfx()

    # Calcul des valeurs relatives en fonction de la resolution
    responsive = responsive_values(screen.get_width(), screen.get_height())

    # chargement de la police de caracteres
    font_lib = font(responsive)

    # Valeurs initiales
    app_values = application_values(screen, responsive)

    # Position initiale de la souris
    if not app_param.use_mouse:
        pygame.mouse.set_visible(False)
        pygame.mouse.set_pos(screen.get_width()/2, screen.get_height()/2)

    if not app_param.no_sound: pygame.mixer.Channel(0).play(sfx_lib.start_sound)

    pygame_task = loop.run_in_executor(None, pygame_event_loop, loop, event_queue)
    animation_task = asyncio.ensure_future(animation(screen, app_param, app_values, font_lib, responsive, sfx_lib))
    event_task = asyncio.ensure_future(handle_events(event_queue, screen, app_param, app_values, responsive, sfx_lib))
    if app_param.use_gpio: gpio_task = asyncio.ensure_future(handle_gpio(event_queue, screen, app_param, app_values, responsive, sfx_lib))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        pygame_task.cancel()
        animation_task.cancel()
        event_task.cancel()
        if app_param.use_gpio: gpio_task.cancel()

    pygame.quit()

# ############################################################################################################################################################
# Launch main
# ############################################################################################################################################################

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
