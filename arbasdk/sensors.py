"""
    Arbalet - ARduino-BAsed LEd Table
    sensor - Arbalet Sensor Manager

    Generates events for sensors such as joysticks, keyboards and touch screen

    Copyright 2016 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from threading import RLock
from arbasdk import Arbapixel, Arbamodel

__all__ = ['CapacitiveTouch', 'MODE_OFF', 'MODE_BI_DIRECTIONAL', 'MODE_TRI_DIRECTIONAL', 'MODE_QUADRI_DIRECTIONAL', 'MODE_COLUMNS', 'MODE_INDIVIDUAL']

MODE_OFF = 0
MODE_BI_DIRECTIONAL = 2
MODE_TRI_DIRECTIONAL = 3
MODE_QUADRI_DIRECTIONAL = 4
MODE_COLUMNS = 5
MODE_INDIVIDUAL = 6


class CapacitiveTouch(object):
    def __init__(self, touch_mode=MODE_OFF):
        self.num_buttons = 6  # Number of touch buttons
        self._previous_state = [False]*self.num_buttons
        self._touch_events = []
        self._events_lock = RLock()
        self._mode = None
        self.set_mode(touch_mode)
        self._model = Arbamodel(15, 10, 'black')
        self._keypad = True

    def set_mode(self, new_mode):
        """
        Activate a helper mode by choosing a set of keys to detect
        """
        if new_mode in [MODE_OFF, MODE_BI_DIRECTIONAL, MODE_TRI_DIRECTIONAL, MODE_QUADRI_DIRECTIONAL, MODE_COLUMNS, MODE_INDIVIDUAL]:
            self._mode = new_mode
        else:
            raise ValueError("Mode {} is not known to {}".format(new_mode, __file__))
        self.update_model()

    def set_keypad(self, enabled=True):
        self._keypad = enabled

    def create_event(self, touch):
        """
        Create the event associated to the specified touch state
        """
        def touch_to_buttons(touch):
            return [(touch & (1 << bit)) > 0 for bit in range(self.num_buttons)]

        state = touch_to_buttons(touch)
        with self._events_lock:
            for button in range(self.num_buttons):
                if state[button] == self._previous_state[button]:
                    continue
                event = { 'id': button+1, 'pressed': state[button] }
                self._touch_events.append(event)
        self._previous_state = state

        # Update the model according to this event
        self.update_model()

    def update_model(self):
        if self._mode != MODE_OFF:
            mapping = self.get_mapping(self._mode)
            with self.model:
                for key, meaning in mapping.iteritems():
                    if meaning is not None:
                        pixels = self.get_pixels_of_keys(self._mode)[key]
                        for pixel in pixels:
                            color = self.get_color_active() if self._previous_state[key-1] else self.get_color()
                            self.model.set_pixel(pixel[0], pixel[1], color)

    def get_mapping(self, mode):
        if mode == MODE_BI_DIRECTIONAL:
            return { 1: None, 2: 'left', 3: 'right', 4: 'left', 5: None, 6: 'right' }
        elif mode == MODE_TRI_DIRECTIONAL:
            return { 1: 'up', 2: None, 3: None, 4: 'left', 5: None, 6: 'right' }
        elif mode == MODE_QUADRI_DIRECTIONAL:
            return { 1: 'up', 2: 'left', 3: 'right', 4: 'left', 5: 'down', 6: 'right' }
        elif mode == MODE_COLUMNS:
            return { 1: None, 2: 2, 3: 4, 4: 1, 5: 3, 6: 5 }
        else:
            return { 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6 }

    def get_pixels_of_keys(self, mode):
        return { 1: [(12, 4), (12, 5)],
                 2: [(13, 2), (13, 3)],
                 3: [(13, 6), (13, 7)],
                 4: [(14, 0), (14, 1)],
                 5: [(14, 4), (14, 5)],
                 6: [(14, 8), (14, 9)] }

    def get_color(self):
        return Arbapixel([20, 20, 20])

    def get_color_active(self):
        return Arbapixel([80, 75, 75])

    def get(self):
        mapping = self.get_mapping(self._mode)

        with self._events_lock:
            events = self.map_events(self._touch_events, mapping)
            self._touch_events = []
        return events

    def map_events(self, raw_events, mapping):
        events = []
        for event in raw_events:
            meaning = mapping[event['id']]
            down = event['pressed']
            if meaning is not None:
                events.append({ 'key': meaning,
                                'type': 'down' if down else 'up' })
        return events

    @property
    def model(self):
        # TODO: Model not thread-safe
        if self._keypad:
            return self._model
        else:
            return Arbamodel(15, 10, 'black')
