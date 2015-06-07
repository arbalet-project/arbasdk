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
from threading import RLock

__all__ = ['Arbamodel']

class Arbamodel(object):
    # line, column
    def __init__(self, height, width, color):
        self.height = height
        self.width = width

        self._model_lock = RLock()
        self._model = [[Arbapixel(color) if len(color)>0 else Arbapixel('black') for j in range(width)] for i in range(height)]

    def copy(self):
        return deepcopy(self)

    def lock(self):
        self._model_lock.acquire()

    def unlock(self):
        self._model_lock.release() # throws RuntimeError if an unlock attempt is made while not locked

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_pixel(self, h, w):
        return self._model[h][w]

    def set_pixel(self, h, w, color):
        self._model[h][w] = Arbapixel(color)

    def get_all_combinations(self):
        return map(tuple, product(range(self.height), range(self.width)))

    def set_all(self, color):
        for w in range(self.width):
            for h in range(self.height):
                self.set_pixel(h, w, color)

    def __add__(self, other):
        model = Arbamodel(self.height, self.width)
        for w in range(self.width):
            for h in range(self.height):
                model._model[h][w] = self._model[h][w] + other.state[h][w]
        return model

    def __eq__(self, other):
        for w in range(self.width):
            for h in range(self.height):
                if self._model[h][w] != other.state[h][w]:
                    return False
        return True

    def __sub__(self, other):
        model = Arbamodel(self.height, self.width)
        for w in range(self.width):
            for h in range(self.height):
                model._model[h][w] = self._model[h][w] - other.state[h][w]
        return model

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self._model)

    def __mul__(self, m):
        model = Arbamodel(self.height, self.width)
        for w in range(self.width):
            for h in range(self.height):
                model._model[h][w] = self._model[h][w]*m
        return model

    def to_json(self):
        return [[p.to_json() for p in self._model[num_row]] for num_row, row in enumerate(self._model)]

    def from_json(self, json_model):
        height = len(json_model)
        width = len(json_model[0]) if height>0 else 0
        if height!=self.get_height() or width!=self.get_width():
            raise ValueError("Data received have size [{}, {}] while model expects [{}, {}]".format(height, width, self.get_height(), self.get_width()))
        for w in range(width):             # TODO Find sth more efficient that constructing objects and browsing lists so much
            for h in range(height):
                self.set_pixel(h, w, json_model[h][w])