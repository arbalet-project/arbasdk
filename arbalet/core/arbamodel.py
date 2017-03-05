"""
    Arbalet - ARduino-BAsed LEd Table
    Model - Arbalet State

    Store a snapshot of the table state

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import numpy as np
from copy import deepcopy
from itertools import product
from threading import RLock
from ..colors import name_to_rgb
from ..animations.message import Message
from ..animations.flash import Flash

__all__ = ['Model']


class Model(object):
    # line, column
    def __init__(self, height, width, color=(0, 0, 0), animations=True):
        self.height = height
        self.width = width
        self.font = None

        self._model_lock = RLock()

        if isinstance(color, str):
            color = name_to_rgb(color)
        self._model = np.tile(color, (height, width, 1)).astype(float)

        if animations:
            self.load_animations()
        else:
            self.animations = {}

    def load_animations(self):
        self.animations = {
            'message': Message(self),
            'flash': Flash(self)
        }

    def copy(self):
        return deepcopy(self)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_pixel(self, h, w):
        return self._model[h, w]

    @property
    def data_frame(self):
        return np.clip((255*self._model).astype(int), 0, 255)

    def set_pixel(self, h, w, color):
        if isinstance(color, str):
            color = name_to_rgb(color)
        self._model[h, w] = color

    def set_line(self, h, color):
        if isinstance(color, str):
            color = name_to_rgb(color)
        for w in range(self.width):
            self._model[h, w] = color

    def set_column(self, w, color):
        if isinstance(color, str):
            color = name_to_rgb(color)
        for h in range(self.height):
            self._model[h, w] = color

    def get_all_combinations(self):
        return map(tuple, product(range(self.height), range(self.width)))

    def set_all(self, color):
        if isinstance(color, str):
            color = name_to_rgb(color)
        for w in range(self.width):
            for h in range(self.height):
                self._model[h, w] = color

    def __enter__(self):
        self._model_lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._model_lock.release()

    def __add__(self, other):
        m = Model(self.height, self.width, animations=False)
        m._model = self._model + other._model
        return m

    def __eq__(self, other):
        return (self._model == other._model).all()

    def __sub__(self, other):
        m = Model(self.height, self.width, animations=False)
        m._model = self._model - other._model
        return m

    def __repr__(self):
        return repr(self._model)

    def __str__(self):
        return str(self._model)

    def __mul__(self, scalar):
        m = Model(self.height, self.width, animations=False)
        m._model = scalar*self._model
        return m

    def to_dict(self):
        return {'h': self.height, 'w': self.width, 'm': self._model.tolist()}

    def from_dict(self, dict_model):
        # {'h': , 'w': , 'm': }
        self._model = np.array(dict_model['m'])
        self.height = dict_model['h']
        self.width = dict_model['w']

    def flash(self, duration=4., speed=1.5):
        if 'flash' in self.animations:
            self.animations['flash'].flash(duration, speed)
        else:
            print("[Arbalet model animations] Can't flash, animations have not been loaded for this model, please call model.load_animations()")

    def write(self, text, foreground, background='black', speed=10):
        if 'flash' in self.animations:
            self.animations['message'].write(text, foreground, background, speed)
        else:
            print("[Arbalet model animations] Can't write text, animations have not been loaded for this model, please call model.load_animations()")