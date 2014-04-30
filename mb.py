# Nate Collings
# CS 3430 Final project

import sys
import pygame
import math
import pymunk
from entities import Entity
import json

from math import atan2, degrees, pi, sin, cos


FPS = 60
WIDTH = 900
HEIGHT = 900
DT = 1./FPS

WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
BLACK    = (  0,   0,   0)
GREEN =         (  0, 204,   0)

DEFAULT_COLOR = BLACK
HIGHLIGHT_LIGHTER = GREEN
HIGHLIGHT_HEAVIER = RED

BGCOLOR = WHITE
FRICTION = 1
WALLWIDTH = 10

# Directional constants - determines if the char is moving left right or not
LEFT = -1
STATIONARY = 0
RIGHT = 1

# Some various movement related constants
PLAYER_SPEED = 100. *2.
PLAYER_GROUND_ACCEL_TIME = 0.05
PLAYER_GROUND_ACCEL = (PLAYER_SPEED/PLAYER_GROUND_ACCEL_TIME)
PULLING_STR = 3
JUMP_HEIGHT = 30.*10


def main():
    # Pygame initializations
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(BGCOLOR)
    clock = pygame.time.Clock()

    # Pymunk space init
    space = init_space()

    direction = STATIONARY
    jump_v = math.sqrt(2.0 * JUMP_HEIGHT * abs(space.gravity.y)) # Jumping velocity

    # Read in our hero and entity, and add them to our pymunk space
    hero, entities = init_entities()
    add_entity_to_space(space, hero)
    for thing in entities:
        add_entity_to_space(space, thing)

    while True:
        target_vx = 0.0

        for event in pygame.event.get():
            if exiting(event):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                hero.body.velocity.y = jump_v
            elif event.type == pygame.KEYUP and event.key == pygame.K_w:
                hero.body.velocity.y = 0.0

        # Check for movment
        keys = pygame.key.get_pressed()
        if(keys[pygame.K_LEFT] or keys[pygame.K_a]):
            direction = LEFT
            target_vx -= PLAYER_SPEED
            hero.body.velocity.x = target_vx
        if(keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            direction = RIGHT
            target_vx += PLAYER_SPEED
            hero.body.velocity.x = target_vx
        if(keys[pygame.K_r]):
            main()
            sys.exit()

        # Check to see if the mouse is hovering over an interactable object
        highlighted_shape = check_for_mouse_over(screen, space, entities, hero)
        if highlighted_shape:
            # See if we are pushing or pulling on an interactable object
            mouse = pygame.mouse.get_pressed()
            if mouse[2]:
                vx, vy, to_move = push(highlighted_shape, hero)
                to_move.velocity.y = vy
                to_move.velocity.x = vx
            elif mouse[0]:
                vx, vy, to_move = pull(highlighted_shape, hero)
                to_move.velocity.y = vy
                to_move.velocity.x = vx

        screen.fill(BGCOLOR)
        space.step(DT)
        pymunk.pygame_util.draw(screen, space)
        pygame.display.update()
        clock.tick(FPS)


def pull(shape, hero):
    '''
    Method used for pulling on objects. Gets the hero and objects position, and calculates the angle between them.
    Then, it gets the velocity we'll need to head in that direction. Finally, it decides whether we're getting
    pulled towards the object, or if the object is getting pulled towards us, based on the mass.
    '''
    hero_pos = hero.body.position
    obj_pos = shape.shape.body.position
    angle = get_angle(obj_pos, hero_pos)

    scale_x = cos(angle)
    scale_y = sin(angle)

    if hero.mass > shape.mass:
        print 'Pulling object towards you'
        return scale_x*PLAYER_SPEED*PULLING_STR, scale_y*PLAYER_SPEED*PULLING_STR, shape.shape.body
    else:
        print 'Pulling self towards object'
        return scale_x*PLAYER_SPEED*PULLING_STR, scale_y*PLAYER_SPEED*PULLING_STR, hero.body

def push(shape, hero):
    '''
    Method used for pushing on objects. Gets the hero and objects position, and calculates the angle between them.
    Then, it gets the velocity we'll need to head in that direction. Finally, it decides whether we're getting
    pushed away from the object, or if the object is getting pushed away from us, based on the mass of the
    hero and the object..
    '''
    hero_pos = hero.body.position
    obj_pos = shape.shape.body.position
    angle = get_angle(obj_pos, hero_pos)

    scale_x = cos(-angle)
    scale_y = sin(-angle)

    if hero.mass > shape.mass:
        print 'Pushing the object away from you'
        return scale_x*PLAYER_SPEED*PULLING_STR, scale_y*PLAYER_SPEED*PULLING_STR, shape.shape.body
    else:
        print 'Pushing yourself away from the object'
        return scale_x*PLAYER_SPEED*PULLING_STR, scale_y*PLAYER_SPEED*PULLING_STR, hero.body


def get_angle(obj1, obj2):
    '''Some simple trig to get the angle between two points (in this case objects) in our game'''
    dx = obj1.x - obj2.x
    dy = obj1.y - obj2.y
    rads = atan2(dy, dx)
    rads %= 2 * pi
    return degrees(rads)

def check_for_mouse_over(screen, space, shapes, hero):
    '''
    This checks to see if the mouse is hovering over an interactable object. If so, it checks to see if 
    that object is metal. If it is, it sets the highlight on the object depending on the weight. This gives
    a visual representation of what you can interact with, and whether it's heavier or lighter. We go through
    all of the objects in this check so that we can set ones that aren't being hovered over back to the default
    color. This could slow things down if we had tons of objects, but for the sake of this demo it works.
    '''
    mouse_pos = pymunk.pygame_util.get_mouse_pos(screen)
    curr_shape = space.point_query_first(mouse_pos)
    if curr_shape:
        for shape in shapes:
            if shape.shape == curr_shape:
                if hasattr(curr_shape, 'metal'):
                    if hero.mass > shape.mass:
                        shape.shape.color = HIGHLIGHT_LIGHTER
                    else:
                        shape.shape.color = HIGHLIGHT_HEAVIER
                    return shape
            else:
                shape.shape.color = DEFAULT_COLOR
    else:
        for shape in shapes:
            shape.shape.color = DEFAULT_COLOR
    return None
    

def init_entities():
    '''Opens and parses the json file that contains the hero and object information.'''
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
    '''Shoves the entity into the pymunk space'''
    space.add(entity.body, entity.shape)

def init_space():
    '''Initializes the pymunk space, and places some walls around the edges.'''
    space = pymunk.Space()
    space.gravity = 0, -1000
    walls = [
        pymunk.Segment(space.static_body, (0, 5), (0, HEIGHT), WALLWIDTH),
        pymunk.Segment(space.static_body, (0, 5), (WIDTH, 5), WALLWIDTH),
        pymunk.Segment(space.static_body, (0, HEIGHT), (WIDTH, HEIGHT), WALLWIDTH),
        pymunk.Segment(space.static_body, (WIDTH-WALLWIDTH, 5), (WIDTH-WALLWIDTH, HEIGHT), WALLWIDTH),
    ]

    for s in walls:
        s.friction = FRICTION
        s.group = 1
        s.color = BLACK
    space.add(walls)

    return space

def exiting(event):
    '''Checks to see if a quit event has occured -- either the escape key or q'''
    if event.type == pygame.QUIT or \
        event.type == pygame.KEYDOWN and (event.key in [pygame.K_ESCAPE, pygame.K_q]):
            return True
    return False



if __name__ == '__main__':
    main()