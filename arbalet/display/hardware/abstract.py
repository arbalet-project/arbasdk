"""
    Arbalet - ARduino-BAsed LEd Table

    Arbalet Display Server: Abstract class representing a device
    Gathers all models and layers from D-Bus, and updates the associated device
    Copyright 2017 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from __future__ import print_function  # py2 stderr
from time import sleep
from ...config import ConfigReader
from ...dbus import DBusClient
from ...tools import Rate
from ...core import Model

__all__ = ['AbstractDisplayDevice']


class ModelLayers(object):
    """
    Handle several layers of models
    """
    def __init__(self, hardware_config):
        self.config = hardware_config
        self.model = Model(self.config['height'], self.config['width'])
        self.background = Model(self.config['height'], self.config['width'])

    @property
    def models(self):
        m = self.model + self.background
        return m


class AbstractDisplayDevice(object):
    def __init__(self, host, hardware_config, diminution=1, stop_event=None):
        config_reader = ConfigReader()
        self.config = config_reader.hardware
        self.layers = ModelLayers(self.config)
        self.bus = DBusClient(display_subscriber=True, raw_event_publisher=True, background_subscriber=True, host=host)
        self.stop = stop_event
        self.rate = Rate(self.config['refresh_rate'])

        self._current_device = 0
        self._diminution = diminution

    ###### Methods below must be overriden when implementing a new device
    def connect(self):
        raise NotImplementedError()

    def is_connected(self):
        raise NotImplementedError()

    def get_touch_events(self):
        raise NotImplementedError()

    def read_touch_frame(self):
        raise NotImplementedError()

    def write_led_frame(self, end_model):
        raise NotImplementedError()
    ###### Methods above must be overriden when implementing a new device

    def map_pixel_to_led(self, h, w):
        try:
            return self.config['mapping'][h][w]
        except IndexError as e:
            self.close()
            raise IndexError('Incorrect mapping, please check your configuration file, server exiting...')

    def connect_forever(self):
        success = False
        while not self.is_connected() and self.is_running():
            self.connect()
            sleep(0.5)
            if self.is_connected() or not self.is_running():
                break
        return success


    def work(self):
        # Step 1/2: Update the model from DBus
        model = self.bus.display.recv(blocking=False)
        background = self.bus.background.recv(blocking=False)

        if model is not None:
            self.layers.model.from_dict(model)
        if background is not None:
            self.layers.background.from_dict(background)

        # Step 2/3; Sne dthe model to the device and determine if reading feedback is necessary
        data_follows = self.write_led_frame(self.layers.models)

        # Step 3/3: Read and publish feedback
        if data_follows:
            self.read_touch_frame()

        for e in self.get_touch_events():
            self.bus.raw_events.publish(e)

        self.rate.sleep()

    def is_running(self):
        return self.stop is None or not self.stop.is_set()

    def run(self):
        while self.is_running():
            try:
                if self.is_connected():
                    self.work()
                    self.rate.sleep()
                else:
                    self.connect_forever()
            except KeyboardInterrupt:
                break
        print("[Arbalet Display server] Shutdown initiated, closing...")
        self.close()

    def close(self):
        self.bus.close()
