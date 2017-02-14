"""
    Arbalet - ARduino-BAsed LEd Table
    MPR121-based 6 key touch interface

    Copyright 2016 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from threading import RLock
from ...core import Model
from ...dbus import DBusClient
from ..abstract import AbstractEvents
from numpy import array, mean
from collections import deque
from time import time

__all__ = ['CapacitiveTouchMapper']


class CapacitiveTouchMapper(AbstractEvents):
    modes = ['off', 'bidirectional', 'tridirectional', 'quadridirectional', 'columns', 'individual']
    def __init__(self):
        super(CapacitiveTouchMapper, self).__init__()
        config = self.config_reader.hardware
        self._num_buttons = len(config['touch']['keys']) if config['touch']['num_keys'] > 0 else 0  # 0 button means touch-disabled hardware
        self._dbus = DBusClient(background_publisher=True)
        self._touch_events = []
        self._touch_int = 0  # Last touch state (combination of booleans)
        self._touch_keys_values = []  # Filtered data of last touched keys
        self._touch_keys_booleans = [False]*self._num_buttons
        self._events_lock = RLock()
        self._mode_lock = RLock()
        self._keypad = True
        self._height =  config['height']
        self._width =  config['width']
        self._config = config
        self._model = Model(self._height, self._width, 'black')
        self._mode = 'off'
        self._old_touch_mode = 'off'  # Store the former touch mode to be able to pause or resume the touch capability
        self._windowed_touch_values = deque([])  # Store the former touch keys values
        self._calibrated_low_levels = []  # Stores the "low level" = untouched
        self.set_mode('quadridirectional') # TODOOOO
        self.plots = []

    def set_mode(self, new_mode):
        """
        Activate a helper mode by choosing a set of keys to detect
        """
        if new_mode in self.modes:
            if self._num_buttons > 0:
                with self._mode_lock:
                    self._mode = new_mode
        else:
            raise ValueError("Mode {} is unknown, should be one of {}".format(new_mode, str(self.modes)))
        self.update_model()

    def set_keypad(self, enabled=True):
        self._keypad = enabled

    def update_calibrated_state(self, button, pressed):
        pressed = bool(pressed)  # Get rid of numpy bools
        if not self._touch_keys_booleans[button] and pressed or self._touch_keys_booleans[button] and not pressed:
            event = self._make_event(button, pressed)
            self._touch_events.append(event)
            self._touch_keys_booleans[button] = pressed

    def get_touch_frame(self):
        """
        Return the low-level touch frame consisting into a touch int and a list of filtered values for each touch key in calibrated mode
        :return: (touch_int, touch_key_booleans]
        """
        return self._touch_int, self._touch_keys_booleans

    def update_model(self):
        with self._mode_lock:
            if self._mode == 'off' or self._num_buttons == 0 or not self._keypad:
                self.model.set_all('black')
            else:
                mapping = self._config['touch']['mapping'][self._mode]
                with self._model:
                    for key, meaning in enumerate(mapping):
                        if meaning is not None:
                            pixels = self._config['touch']['keys'][key]
                            for pixel in pixels:
                                if self._config['touch']['mapping'][self._mode][key] != 'none':
                                    color = self._config['touch']['colors']['active'] if self._touch_keys_booleans[key] else self._config['touch']['colors']['inactive']
                                    self._model.set_pixel(pixel[0], pixel[1], color)
        self._dbus.background.publish(self._model.to_dict())
        print self._model.to_dict()

    def _make_event(self, button, pressed):
        with self._mode_lock:
            if self._mode == 'off':
                return None
            mapping = self._config['touch']['mapping'][self._mode]

        meaning = mapping[button]
        if meaning != 'none':
            return {'key': meaning,
                    'device': {'type': 'touch', 'id': 'hardware'},
                    'player': 0,
                    'pressed': pressed,
                    'time': time()}

    def map(self, raw_event):
        """
        Returns the 0 (None), 1 (dict), or N (list of dicts) events associated to the specified touch state, and, if calibration enable, to the list of filtered keys data
        :param raw_event: {u'touch_int': 0, u'type': u'capacitive_touch', u'touch_keys': [int]*num_keys}
        """
        def touch_to_buttons(touch):
            return [(touch & (1 << bit)) > 0 for bit in range(self._num_buttons)]

        touch = raw_event['touch_int']
        keys = raw_event['touch_keys']

        if self._config['touch']['num_keys'] < 1 or self._mode == 'off':
            return None

        if self._config['touch']['calibrated'] and len(keys) == self._num_buttons:
            # Strategy: compare the mean of the last 10 samples
            self._windowed_touch_values.append(keys)
            if len(self._windowed_touch_values) > self._config['touch']['window_size']:
                self._windowed_touch_values.popleft()
                windowed_mean = mean(array(self._windowed_touch_values), axis=0)

                if len(self._calibrated_low_levels) == 0:
                    # If uncalibrated
                    self._calibrated_low_levels = windowed_mean
                    print("[Capacitive Touch sensor] Touch calibrated")
                else:
                    # If calibration done
                    for button in range(self._num_buttons):
                        diff = windowed_mean[button] - self._calibrated_low_levels[button]
                        self.update_calibrated_state(button, diff < -self._config['touch']['threshold'])
        else:
            # Strategy: use the "touch" int computed by the Arduino's lib
            state = touch_to_buttons(touch)
            with self._events_lock:
                for button in range(self._num_buttons):
                    if state[button] == self._touch_keys_booleans[button]:
                        continue

                    event = self._make_event(button, state[button])
                    self._touch_events.append(event)
            self._touch_keys_booleans = state

        # Update the model according to this event
        self.update_model()

        self._touch_int = touch
        self._touch_keys_values = keys
        events = self._touch_events
        self._touch_events = []
        return events

    def toggle_touch(self):
        """
        Temporarily pause or restore the touch feature
        If this application is not touch compatible, this method has no effect since it will switch between off and
        """
        current_mode = self._mode
        self.set_mode(self._old_touch_mode)
        self._old_touch_mode = current_mode

    @property
    def model(self):
        return self._model

    @property
    def mode(self):
        return self._mode