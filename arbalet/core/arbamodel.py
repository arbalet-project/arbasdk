"""
    Arbalet - ARduino-BAsed LEd Table
    Arbamodel - Arbalet State

    Store a snapshot of the table state

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from .arbapixel import Arbapixel
from copy import deepcopy
from itertools import product
from threading import RLock
from .arbafont import Arbafont
from .rate import Rate

__all__ = ['Arbamodel']

class Arbamodel(object):
    # line, column
    def __init__(self, height, width, color):
        self.height = height
        self.width = width
        self.font = None

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

    def __enter__(self):
        self.lock()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unlock()

    def __add__(self, other):
        model = Arbamodel(self.height, self.width, 'black')
        for w in range(self.width):
            for h in range(self.height):
                model._model[h][w] = self._model[h][w] + other._model[h][w]
        return model

    def __eq__(self, other):
        for w in range(self.width):
            for h in range(self.height):
                if self._model[h][w] != other._model[h][w]:
                    return False
        return True

    def __sub__(self, other):
        model = Arbamodel(self.height, self.width, 'black')
        for w in range(self.width):
            for h in range(self.height):
                model._model[h][w] = self._model[h][w] - other._model[h][w]
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

    def set_font(self, font=None, vertical=True):
        """
        Instantiate the selected (or the default) font to write on this model
        :param font: Font name (list: pygame.font.get_fonts()
        :param vertical: True if the text must be displayed in portrait mode, false for landscape mode
        """
        self.font = Arbafont(self.height, self.width, vertical, font)

    def write(self, text, foreground, background='black', speed=10):
        """
        Blocking and self-locking call writing text to the model until scrolling is complete
        :param text: an UTF-8 string representing the text to display
        :param foreground: foreground color
        :param background: background color
        :param speed: frequency of update (Hertz)
        """
        if self.font is None:
            self.set_font()

        rendered = self.font.render(text)
        rate = Rate(speed)
        if self.font.vertical:
            scrolling_range = range(len(rendered.rendered[0]))
        else:
            scrolling_range = range(len(rendered.rendered), 0, -1)

        for start in scrolling_range:
            with self:
                for h in range(self.height):
                    for w in range(self.width):
                        try:
                            illuminated = rendered.rendered[h if self.font.vertical else h+start][w+start if self.font.vertical else w]
                        except IndexError:
                            illuminated = False
                        self.set_pixel(h, w, foreground if illuminated else background)
            rate.sleep()
