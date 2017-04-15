"""
    Arbalet - ARduino-BAsed LEd Table
    RPiLink - Arbalet Link to the hardware table using SPI 0 MOSI on Raspberry Pi

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from __future__ import print_function  # py2 stderr
from .abstract import AbstractDisplayDevice
import numpy as np

__all__ = ['RPiLink']

try:
    import spidev
    from neopixel import Adafruit_NeoPixel, Color
except ImportError as e:
    pass


class RPiSPIDisplayServer(AbstractDisplayDevice):
    def __init__(self, host, hardware_config, diminution=1):
        super(RPiSPIDisplayServer, self).__init__(host, hardware_config, diminution)
        self._connected = False
        self.check_import()
        brightness = min(255, max(1, int(255*diminution)))  # TODO take into account
        self.count = self.config['height'] * self.config['width']
        self.count_spi_bytes = self.count*3
        self.data = np.zeros(self.count_spi_bytes, dtype=np.uint8)
        self.tx = np.zeros(self.count_spi_bytes * 4, dtype=np.uint8)
        self.spi = spidev.SpiDev()
        self.speed = self.config["spi"]["speed"]

    def check_import(self):
        # Check import only if this driver has been instanciated
        try:
            cls = spidev
        except NameError as e:
            raise ImportError("No spidev found, make sure you have pulled and installed the git submodule py-spidev")

    def is_connected(self):
        return self._connected

    def connect(self):
        self.spi.open(self.config['spi']['bus'], self.config['spi']['device'])
        self._connected = True

    def get_touch_events(self):
        return []

    def write2812(self):
        """
        From https://github.com/joosteto/ws2812-spi
        """
        for ibit in range(4):
            self.tx[3 - ibit::4] = ((self.data >> (2 * ibit + 1)) & 1) * 0x60 + ((self.data >> (2 * ibit + 0)) & 1) * 0x06 + 0x88

        self.spi.xfer(self.tx.tolist(), self.speed)

    def write_led_frame(self, end_model):
        frame = end_model.data_frame
        for h in range(end_model.get_height()):
            for w in range(end_model.get_width()):
                index = self.map_pixel_to_led(h, w)

                r, g, b = frame[h][w][0], frame[h][w][1], frame[h][w][2]
                self.data[index*3] = g
                self.data[index*3+1] = r
                self.data[index*3+2] = b
        self.write2812()


class RPiPWMDisplayServer(AbstractDisplayDevice):
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA = 5  # DMA channel to use for generating signal (try 5)
    LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)

    def __init__(self, host, hardware_config, diminution=1):
        super(RPiPWMDisplayServer, self).__init__(host, hardware_config, diminution)
        self._connected = False
        self.check_import()
        brightness = min(255, max(1, int(255*diminution)))
        count = self.config['width'] * self.config['height']
        led_pin = 18
        self.leds = Adafruit_NeoPixel(count, led_pin, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, brightness)

    def check_import(self):
        # Check import only if this driver has been instanciated
        try:
            cls = Adafruit_NeoPixel
        except NameError as e:
            raise ImportError("Can't import rpi_ws281x, get it from https://github.com/ymollard/rpi_ws281x")

    def is_connected(self):
        return self._connected

    def connect(self):
        try:
            self.leds.begin()
        except RuntimeError as e:
            raise RuntimeError(repr(e) +
                               "\nWS2811 driver for RPi requires root permissions, are you actually root?"
                               "\nAlso make sure that PIN{} is PWM-capable".format(self.config['leds_pin_number']))
        else:
            self._connected = True

    def get_touch_events(self):
        return []

    def write_led_frame(self, end_model):
        for h in range(end_model.get_height()):
            for w in range(end_model.get_width()):
                rgb = end_model._model[h][w][0], end_model._model[h][w][1], end_model._model[h][w][2]
                r, g, b = map(lambda x: int(255*x), rgb)
                self.leds.setPixelColor(self.map_pixel_to_led(h, w), Color(g, r, b))
        self.leds.show()

