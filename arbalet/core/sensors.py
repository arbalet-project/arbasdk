"""
    Arbalet - ARduino-BAsed LEd Table
    sensor - Arbalet Sensor Manager

    Generates events for sensors such as joysticks, keyboards and touch screen

    Copyright 2016 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from threading import RLock
from arbalet.core import Arbamodel
from json import load
from numpy import array, mean
from collections import deque
__all__ = ['CapacitiveTouch']

class CapacitiveTouch(object):
    modes = ['off', 'bidirectional', 'tridirectional', 'quadridirectional', 'columns', 'individual']
    def __init__(self, config, height, width, touch_mode='off'):
        with open(config) as f:
            self._config = load(f)

        self._num_buttons = len(self._config['touch']['keys']) if self._config['touch']['num_keys'] > 0 else 0  # 0 button means touch-disabled hardware
        self._touch_events = []
        self._touch_int = 0  # Last touch state (combination of booleans)
        self._touch_keys_values = []  # Filtered data of last touched keys
        self._touch_keys_booleans = [False]*self._num_buttons
        self._events_lock = RLock()
        self._mode_lock = RLock()
        self._keypad = True
        self._height = height
        self._width = width
        self._model = Arbamodel(self._height, self._width, 'black')
        self._mode = 'off'
        self._old_touch_mode = 'off'  # Store the former touch mode to be able to pause or resume the touch capability
        self._windowed_touch_values = deque([])  # Store the former touch keys values
        self._calibrated_low_levels = []  # Stores the "low level" = untouched
        self.set_mode(touch_mode)
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
        if not self._touch_keys_booleans[button] and pressed or self._touch_keys_booleans[button] and not pressed:
            event = { 'id': button, 'pressed': pressed }
            self._touch_events.append(event)
            self._touch_keys_booleans[button] = pressed

    def create_event(self, touch, keys):
        """
        Entry point of the table connection interface
        Create the event associated to the specified touch state, and, if calibration enable, to the list of filtered keys data
        :param touch: The touch int returned by the Arduino lib (each bit is a boolean)
        :param keys: The filtered values returned by the Arudino lib (int) OR the precalibrated boolean values
        """
        def touch_to_buttons(touch):
            return [(touch & (1 << bit)) > 0 for bit in range(self._num_buttons)]

        if self._config['touch']['num_keys'] < 1:
            # Warning: do not return if mode==off, arbaserver needs to update touch key states in any case
            return

        if self._config['touch']['calibrated']:
            # Strategy: compare the mean of the last 10 samples

            if isinstance(keys[0], bool):
                # Precalibrated by a server (arbaclient case)
                for button in range(self._num_buttons):
                    self.update_calibrated_state(button, keys[button])
            else:
                # Non pre-calibrated (normal case), perform calibration
                self._windowed_touch_values.append(keys)
                if len(self._windowed_touch_values) > self._config['touch']['window_size']:
                    self._windowed_touch_values.popleft()
                    windowed_mean = mean(array(self._windowed_touch_values), axis=0)

                    if len(self._calibrated_low_levels) == 0:
                        # If uncalibrated
                        self._calibrated_low_levels = windowed_mean
                        print("Touch calibrated")
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
                    event = { 'id': button, 'pressed': state[button] }
                    self._touch_events.append(event)
            self._touch_keys_booleans = state

        # Update the model according to this event
        self.update_model()

        self._touch_int = touch
        self._touch_keys_values = keys

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

    def get(self):
        """
        Entry points of apps to get the touch events mapped according to current touch mode
        :return: list of events (dictionary)
        """
        with self._mode_lock:
            if self._mode == 'off':
                return []
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
