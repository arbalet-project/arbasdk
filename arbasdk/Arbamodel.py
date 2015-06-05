"""
    Arbalet - ARduino-BAsed LEd Table
    Arbamodel - Arbalet State

    Store a snapshot of the table state

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from Arbapixel import Arbapixel
from copy import deepcopy
from itertools import product
from threading import Lock

__all__ = ['Arbamodel']

class Arbamodel(object):
    # line, column
    def __init__(self, height, width, *color):
        self.height = height
        self.width = width

        self.model_lock = Lock()
        self.model = [[Arbapixel(*color) if len(color)>0 else Arbapixel('black') for j in range(width)] for i in range(height)]

    def copy(self):
        return deepcopy(self)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_pixel(self, h, w):
        with self.model_lock:
            p = self.model[h][w]
        return p

    def set_pixel(self, h, w, *color):
        with self.model_lock:
            self.model[h][w] = Arbapixel(*color)

    def get_all_combinations(self):
        return map(tuple, product(range(self.height), range(self.width)))

    def set_all(self, *color):
        for w in range(self.width):
            for h in range(self.height):
                self.model[h][w].set_color(*color)

    def __add__(self, other):
        model = Arbamodel(self.height, self.width)
        for w in range(self.width):
            for h in range(self.height):
                model.model[h][w] = self.model[h][w] + other.state[h][w]
        return model

    def __eq__(self, other):
        for w in range(self.width):
            for h in range(self.height):
                if self.model[h][w] != other.state[h][w]:
                    return False
        return True

    def __sub__(self, other):
        model = Arbamodel(self.height, self.width)
        for w in range(self.width):
            for h in range(self.height):
                model.model[h][w] = self.model[h][w] - other.state[h][w]
        return model

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.model)

    def __mul__(self, m):
        model = Arbamodel(self.height, self.width)
        for w in range(self.width):
            for h in range(self.height):
                model.model[h][w] = self.model[h][w]*m
        return model

    def to_json(self):
        return [[p.to_json() for p in self.model[num_row]] for num_row, row in enumerate(self.model)]

    def from_json(self, json_model):
        height = len(json_model)
        width = len(json_model[0]) if height>0 else 0
        if height!=self.get_height() or width!=self.get_width():
            raise ValueError("Data received have size [{}, {}] while model expects [{}, {}]".format(height, width, self.get_height(), self.get_width()))
        for w in range(width):             # TODO Find sth more efficient that constructing objects and browsing lists so much
            for h in range(height):
                self.set_pixel(h, w, *json_model[h][w])