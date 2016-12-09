"""
    Arbalet - ARduino-BAsed LEd Table
    Model - Arbalet State

    Store a snapshot of the table state

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import numpy as np
import json
from copy import deepcopy
from itertools import product
from threading import RLock
from time import time
from .arbafont import Font
from .rate import Rate
from .colors import name_to_rgb

__all__ = ['Model']

class Model(object):
    # line, column
    def __init__(self, height, width, color=None):
        self.height = height
        self.width = width
        self.font = None

        self._model_lock = RLock()
        self._model = np.zeros((height, width, 3), dtype=float)

        if color is not None:
            self.set_all(color)

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
        m = Model(self.height, self.width)
        m._model = self._model + other._model
        return m

    def __eq__(self, other):
        return (self._model == other._model).all()

    def __sub__(self, other):
        m = Model(self.height, self.width)
        m._model = self._model - other._model
        return m

    def __repr__(self):
        return repr(self._model)

    def __str__(self):
        return str(self._model)

    def __mul__(self, scalar):
        m = Model(self.height, self.width)
        m._model = scalar*self._model
        return m

    def to_json(self):
        def to_json(self):
            return json.dumps(self._model.tolist())

    def from_json(self, json_model):
        self._model = json.loads(json_model)
        self.height = self._model.shape[0]
        self.width = self._model.shape[1]

    def set_font(self, font=None, vertical=True):
        """
        Instantiate the selected (or the default) font to write on this model
        :param font: Font name (list: pygame.font.get_fonts()
        :param vertical: True if the text must be displayed in portrait mode, false for landscape mode
        """
        self.font = Font(self.height, self.width, vertical, font)

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

    def flash(self, duration=4., speed=1.5):
        """
        Blocking and self-locking call flashing the current model on and off (mainly for game over)
        :param duration: Approximate duration of flashing in seconds
        :param rate: Rate of flashing in Hz
        """
        rate = Rate(speed)
        t0 = time()
        model_id = 0
        with self._model_lock:
            models = [np.zeros((self.height, self.width, 3)), self._model]

        model_off = False
        while time()-t0 < duration or model_off:
            with self._model_lock:
                self._model = models[model_id]
            model_id = (model_id + 1) % 2
            model_off = not model_off
            rate.sleep()