# Copyright 2021 Google LLC
# SPDX-License-Identifier: Apache-2.0
# https://www.apache.org/licenses/LICENSE-2.0
import pygame
from pygame.locals import *
import os
import random

class Bubble:
    def __init__(self,location, size):
        self.location=location
        self.size = size
        self.color = (0,0,255)
        self.thickness = 0

        self.velocity = [0,0] # velocity x, y
        self.accel = [0,0] # acceleration x, y

        self.shrink = 0
        self.exists = True

    def update(self):
        self.location = [self.location[i]+self.velocity[i] for i in range(0,2)]
        self.velocity = [self.velocity[i]+self.accel[i] for i in range(0,2)]
        self.size += self.shrink

        w, h = pygame.display.get_surface().get_size()
        if (self.location[0] < -10 or self.location[0] > w +10 or self.location[1] < -10 or self.location[1] > h+10):
            self.exists  = False  # off the edge of the board
        if (self.size <= 0):
            self.exists = False # shrunk to nothing

    def display(self,screen):
        thickness = 0
        if (self.thickness < self.size):
            thickness = self.thickness
        if (self.exists):
            pygame.draw.circle(screen, self.color, [int(self.location[0]), int(self.location[1])], self.size,int(thickness))



if __name__ == '__main__':
    # a clock for controlling the fps later
    clock = pygame.time.Clock()

    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))

    running = True
    bubbles = []
    click = False
    colors = ["red","blue","orange","green","yellow","pink"]
    while running:
        screen.fill((0,0,0))

        mx, my = pygame.mouse.get_pos()

        if (click):
            for i in range(10):
                bubble = Bubble([mx,my],random.randint(5,40))
                bubble.velocity = [random.randint(-20,20)/7,random.randint(-20,20)/6]
                bubble.accel = [0,0.02]  # downwards acceleration
                bubble.thickness = 0
                bubble.shrink= -0.2
                idx = random.randint(0,len(colors)-1)
                bubble.color = colors[idx]
                bubbles.append(bubble)
        #click = False

        for bubble in bubbles:
            bubble.update()
            if (bubble.exists == False):
                bubbles.remove(bubble)

        for bubble in bubbles:
            bubble.display(screen)


        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                   click = False