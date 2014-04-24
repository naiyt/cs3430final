import sys
import pygame
import math
import pymunk
from pymunk.vec2d import Vec2d
from pymunk.pygame_util import draw, from_pygame, to_pygame

class Entity:
    def __init__(self, mass, size, color, start, name='Fred', metal=True, friction=1):
        self.mass = mass
        self.size = size
        self.color = color
        self.metal = metal
        self.start = start
        self.name = name
        self.friction = friction
        self.points = [(-size, -size), (-size, size), (size,size), (size, -size)]
        self.moment = pymunk.moment_for_poly(self.mass, self.points, (0, 0))

        self._init_shape()


    def _init_shape(self):
        self.body = pymunk.Body(self.mass, self.moment)
        self.body.position = self.start
        self.shape = pymunk.Poly(self.body, self.points, (0,0))
        self.shape.friction = self.friction
        self.shape.color = self.color
        self.shape.metal = self.metal
        

