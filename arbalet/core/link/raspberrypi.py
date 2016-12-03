"""
    Arbalet - ARduino-BAsed LEd Table
    RPiLink - Arbalet Link to the hardware table using PWM on Raspberry Pi

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from __future__ import print_function  # py2 stderr
from .abstract import AbstractLink

__all__ = ['RPiLink']

try:
    from neopixel import Adafruit_NeoPixel, Color
except ImportError as e:
    pass


class RPiLink(AbstractLink):
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA = 5  # DMA channel to use for generating signal (try 5)
    LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
    LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)

    def __init__(self, arbalet, diminution=1):
        super(RPiLink, self).__init__(arbalet, diminution)
        self._connected = False
        self.check_import()
        brightness = min(255, max(1, int(255*diminution)))
        count = arbalet.width * arbalet.height
        led_pin = self._arbalet.config['leds_pin_number']
        self.leds = Adafruit_NeoPixel(count, led_pin, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, brightness)
        self.start()

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
                               "\nAlso make sure that PIN{} is PWM-capable".format(self._arbalet.config['leds_pin_number']))
        else:
            self._connected = True

    def read_touch_frame(self):
        pass

    def write_led_frame(self, end_model):
        for h in range(end_model.get_height()):
            for w in range(end_model.get_width()):
                r, g, b = end_model._model[h][w][0], end_model._model[h][w][1], end_model._model[h][w][2]
                self.leds.setPixelColor(self.map_pixel_to_led(h, w), Color(g, r, b))
        self.leds.show()
