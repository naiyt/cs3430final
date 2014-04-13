import sys
import pygame

import pymunk
from pymunk.vec2d import Vec2d
from pymunk.pygame_util import draw, from_pygame, to_pygame


FPS = 60
WIDTH = 800
HEIGHT = 800
DT = 1./FPS

WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
BLACK    = (  0,   0,   0)

BGCOLOR = WHITE
FRICTION = 1
WALLWIDTH = 10

START_POS = (35, 500)

LEFT = -1
RIGHT = 1

PLAYER_VELOCITY = 100. *2.
PLAYER_GROUND_ACCEL_TIME = 0.05
PLAYER_GROUND_ACCEL = (PLAYER_VELOCITY/PLAYER_GROUND_ACCEL_TIME)

def main():

    # Pygame initializations
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(BGCOLOR)

    clock = pygame.time.Clock()
    running = True

    # Pymunk initializations
    space = pymunk.Space()
    space.gravity = 0, -1000
    static = [
        pymunk.Segment(space.static_body, (0, 5), (0, HEIGHT), WALLWIDTH),
        pymunk.Segment(space.static_body, (0, 5), (WIDTH, 5), WALLWIDTH),
        pymunk.Segment(space.static_body, (0, HEIGHT), (WIDTH, HEIGHT), WALLWIDTH),
        pymunk.Segment(space.static_body, (WIDTH-WALLWIDTH, 5), (WIDTH-WALLWIDTH, HEIGHT), WALLWIDTH),
    ]

    for s in static:
        s.friction = FRICTION
        s.group = 1
        s.color = BLACK
    space.add(static)

    # Player init

    size = 12
    points = [(-size, -size), (-size, size), (size,size), (size, -size)]
    mass = 5.0
    body = pymunk.Body(mass, pymunk.inf)
    body.position = START_POS
    shape = pymunk.Poly(body, points, (0,0))
    shape.friction = 1
    space.add(body, shape)

    direction = 0

    while running:
        for event in pygame.event.get():
            if exiting(event):
                pygame.quit()
                sys.exit()

        target_vx = 0

        keys = pygame.key.get_pressed()
        if(keys[pygame.K_LEFT]):
            direction = LEFT
            target_vx -= PLAYER_VELOCITY
        if(keys[pygame.K_RIGHT]):
            direction = RIGHT
            target_vx += PLAYER_VELOCITY

        body.velocity.x = target_vx

        screen.fill(BGCOLOR)
        space.step(DT)
        draw(screen, space)
        pygame.display.update()
        clock.tick(FPS)



# Check to see if a quit event has occured
def exiting(event):
    if event.type == pygame.QUIT or \
        event.type == pygame.KEYDOWN and (event.key in [pygame.K_ESCAPE, pygame.K_q]):
            return True
    return False



if __name__ == '__main__':
    main()