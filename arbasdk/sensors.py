"""
    Arbalet - ARduino-BAsed LEd Table
    sensor - Arbalet Sensor Manager

    Generates events for sensors such as joysticks, keyboards and touch screen

    Copyright 2016 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from threading import RLock
from arbasdk import Arbamodel
from json import load

__all__ = ['CapacitiveTouch']

class CapacitiveTouch(object):
    modes = ['off', 'bidirectional', 'tridirectional', 'quadridirectional', 'columns', 'individual']
    def __init__(self, config, height, width, touch_mode='off'):
        with open(config) as f:
            self._config = load(f)

        self._num_buttons = len(self._config['touch']['keys']) if self._config['touch']['enabled'] else 0  # 0 button means touch-disabled hardware
        self._previous_state = [False]*self._num_buttons
        self._touch_events = []
        self._events_lock = RLock()
        self._keypad = True
        self._height = height
        self._width = width
        self._model = Arbamodel(self._height, self._width, 'black')
        self._mode = None
        self.set_mode(touch_mode)

    def set_mode(self, new_mode):
        """
        Activate a helper mode by choosing a set of keys to detect
        """
        if new_mode in self.modes:
            self._mode = new_mode
        else:
            raise ValueError("Mode {} is unknown, should be one of {}".format(new_mode, str(self.modes)))
        self.update_model()

    def set_keypad(self, enabled=True):
        self._keypad = enabled

    def create_event(self, touch):
        """
        Create the event associated to the specified touch state
        """
        def touch_to_buttons(touch):
            return [(touch & (1 << bit)) > 0 for bit in range(self._num_buttons)]

        state = touch_to_buttons(touch)
        with self._events_lock:
            for button in range(self._num_buttons):
                if state[button] == self._previous_state[button]:
                    continue
                event = { 'id': button, 'pressed': state[button] }
                self._touch_events.append(event)
        self._previous_state = state

        # Update the model according to this event
        self.update_model()

    def update_model(self):
        if self._mode == 'off' or self._num_buttons == 0 or not self._keypad:
            self.model.set_all('black')
        else:
            mapping = self._config['touch']['mapping'][self._mode]
            with self._model:
                for key, meaning in enumerate(mapping):
                    if meaning is not None:
                        pixels = self._config['touch']['keys'][key]
                        for pixel in pixels:
                            color = self._config['touch']['colors']['active'] if self._previous_state[key] else self._config['touch']['colors']['inactive']
                            self._model.set_pixel(pixel[0], pixel[1], color)

    def get(self):
        mapping = self._config['touch']['mapping'][self._mode]

        with self._events_lock:
            events = self.map_events(self._touch_events, mapping)
            self._touch_events = []
        return events

    def map_events(self, raw_events, mapping):
        events = []
        for event in raw_events:
            meaning = mapping[event['id']]
            down = event['pressed']
            if meaning != 'none':
                events.append({ 'key': meaning,
                                'type': 'down' if down else 'up' })
        return events

    @property
    def model(self):
        return self._model

