"""
    Arbalet - ARduino-BAsed LEd Table
    AbstractLink - Abstract class for hardware LED controllers

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from __future__ import print_function  # py2 stderr
from threading import Thread
from time import sleep
from ...tools import Rate

__all__ = ['AbstractLink']


class AbstractLink(Thread):
    def __init__(self, layers, hardware_config, diminution=1):
        """
        Create a thread in charge of the serial connection to hardware
        :param layers: The ModelLayers object to request the end model to
        :param hardware_config: The hardware configuration
        :param diminution: Brightness of the table from 0.0 to 1.0
        """
        Thread.__init__(self)
        self.setDaemon(True)
        self._current_device = 0
        self._diminution = diminution
        self._layers = layers
        self._running = True
        self._config = hardware_config
        self._rate = Rate(self._config['refresh_rate'])


    def connect(self):
        raise NotImplementedError()

    def connect_forever(self):
        success = False
        while not self.is_connected():
            self.connect()
            if self.is_connected():
                break
            sleep(0.5)
        return success

    def is_connected(self):
        raise NotImplementedError()

    def close(self):
        self._running = False

    def map_pixel_to_led(self, h, w):
        try:
            return self._config['mapping'][h][w]
        except IndexError as e:
            self.close()
            raise IndexError('Incorrect mapping, please check your configuration file, arbalink exiting...')

    def get_touch_events(self):
        raise NotImplementedError()

    def read_touch_frame(self):
        raise NotImplementedError()

    def write_led_frame(self, end_model):
        raise NotImplementedError()

    def run(self):
        while (self._running):
            if self.is_connected():
                data_follows = self.write_led_frame(self._layers.models)
                if data_follows:
                    self.read_touch_frame()
                self._rate.sleep()
            else:
                self.connect_forever()
        self.close()
