import sys
import pygame
import math
import pymunk
from pymunk.vec2d import Vec2d
from entities import Entity
import json

FPS = 60
WIDTH = 800
HEIGHT = 800
DT = 1./FPS

WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
BLACK    = (  0,   0,   0)

DEFAULT_COLOR = BLACK
HIGHLIGHT_COLOR = RED

BGCOLOR = WHITE
FRICTION = 1
WALLWIDTH = 10

LEFT = -1
STATIONARY = 0
RIGHT = 1

PLAYER_VELOCITY = 100. *2.
PLAYER_GROUND_ACCEL_TIME = 0.05
PLAYER_GROUND_ACCEL = (PLAYER_VELOCITY/PLAYER_GROUND_ACCEL_TIME)

JUMP_HEIGHT = 30.*3

def main():

    # Pygame initializations
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(BGCOLOR)

    clock = pygame.time.Clock()
    running = True

    # Pymunk space init
    space = init_space()

    direction = STATIONARY
    jump_v = math.sqrt(2.0 * JUMP_HEIGHT * abs(space.gravity.y))

    hero, entities = init_entities()

    add_entity_to_space(space, hero)
    for thing in entities:
        add_entity_to_space(space, thing)

    target_vy = hero.body.velocity.y
    while running:
        target_vx = 0.0

        for event in pygame.event.get():
            if exiting(event):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                hero.body.velocity.y = jump_v
            elif event.type == pygame.KEYUP and event.key == pygame.K_UP:
                hero.body.velocity.y = 0.0


        keys = pygame.key.get_pressed()
        if(keys[pygame.K_LEFT]):
            direction = LEFT
            target_vx -= PLAYER_VELOCITY
        if(keys[pygame.K_RIGHT]):
            direction = RIGHT
            target_vx += PLAYER_VELOCITY
        if(keys[pygame.K_r]):
            main()
            sys.exit()


        highlighted_shape = check_for_mouse_over(screen, space, entities)
        if highlighted_shape:
            if(keys[pygame.K_w]):
                target_vx, target_vy = push(highlighted_shape, hero)
                hero.body.velocity.y = target_vy
            elif keys[pygame.K_s]:
                target_vx, target_vy = pull(highlighted_shape, hero)
                hero.body.velocity.y = target_vy


        hero.body.velocity.x = target_vx

        print hero.body.velocity.y

        screen.fill(BGCOLOR)
        space.step(DT)
        pymunk.pygame_util.draw(screen, space)
        pygame.display.update()
        clock.tick(FPS)


def push(shape, hero):
    print 'pushing {}'.format(shape.name)
    return 100, 100

def pull(shape, hero):
    print 'pulling {}'.format(shape.name)
    return 100, 100

def check_for_mouse_over(screen, space, shapes):
    mouse_pos = pymunk.pygame_util.get_mouse_pos(screen)
    curr_shape = space.point_query_first(mouse_pos)
    if curr_shape:
        for shape in shapes:
            if shape.shape == curr_shape:
                if hasattr(curr_shape, 'metal'):
                    shape.shape.color = HIGHLIGHT_COLOR
                    return shape
            else:
                shape.shape.color = DEFAULT_COLOR
    else:
        for shape in shapes:
            shape.shape.color = DEFAULT_COLOR
    return None
    

def init_entities():
    with open('entities.json') as infile:
        entities_json = json.loads(infile.read())

    hero_info = entities_json['hero']
    hero = Entity(
        hero_info['mass'],
        hero_info['size'],
        DEFAULT_COLOR,
        (hero_info['start_pos']['x'], hero_info['start_pos']['y']),
        hero_info['name']
    )

    entities = []
    for thing in entities_json['interactive_objs'].values():
        new_ent =  Entity(
            thing['mass'],
            thing['size'],
            DEFAULT_COLOR,
            (thing['start_pos']['x'], thing['start_pos']['y']),
            thing['name']
        )
        entities.append(new_ent)

    return hero, entities

def add_entity_to_space(space, entity):
    space.add(entity.body, entity.shape)


def init_space():
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

    return space


# Check to see if a quit event has occured
def exiting(event):
    if event.type == pygame.QUIT or \
        event.type == pygame.KEYDOWN and (event.key in [pygame.K_ESCAPE, pygame.K_q]):
            return True
    return False



if __name__ == '__main__':
    main()