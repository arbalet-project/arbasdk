from ...config import ConfigReader
from ...core import Model
from ...dbus import DBusClient
from threading import RLock


class TouchMapper(object):
    modes = ['off', 'bidirectional', 'tridirectional', 'quadridirectional', 'columns', 'individual']

    def __init__(self):
        self._dbus = DBusClient(background_publisher=True)
        self._config = ConfigReader().hardware
        self._height =  self._config['height']
        self._width =  self._config['width']
        self._num_buttons = len(self._config['touch']['keys']) if self._config['touch']['num_keys'] > 0 else 0  # 0 button means touch-disabled hardware
        self._mode_lock = RLock()
        self._model = Model(self._height, self._width)
        self._keypad = True
        self._mode = 'off'
        self._old_touch_mode = 'off'  # Store the former touch mode to be able to pause or resume the touch capability
        self._touch_keys_booleans = [False]*self._num_buttons
        self.set_mode('quadridirectional')  # TODOOOO

    def set_keypad(self, enabled=True):
        self._keypad = enabled

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