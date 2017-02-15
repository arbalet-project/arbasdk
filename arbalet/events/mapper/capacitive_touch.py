"""
    Arbalet - ARduino-BAsed LEd Table
    MPR121-based 6 key touch interface

    Copyright 2016 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from threading import RLock
from .touch import TouchMapper
from numpy import array, mean
from collections import deque
from time import time

__all__ = ['CapacitiveTouchMapper']


class CapacitiveTouchMapper(TouchMapper):
    def __init__(self):
        super(CapacitiveTouchMapper, self).__init__()
        self._touch_events = []
        self._touch_int = 0  # Last touch state (combination of booleans)
        self._touch_keys_values = []  # Filtered data of last touched keys
        self._events_lock = RLock()
        self._windowed_touch_values = deque([])  # Store the former touch keys values
        self._calibrated_low_levels = []  # Stores the "low level" = untouched

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
