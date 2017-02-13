"""
    Arbalet - ARduino-BAsed LEd Table
    RPiLink - Arbalet Link to the hardware table using SPI 0 MOSI on Raspberry Pi

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from __future__ import print_function  # py2 stderr
from .abstract import AbstractLink
import numpy as np

__all__ = ['RPiLink']

try:
    import spidev
except ImportError as e:
    pass


class RPiLink(AbstractLink):
    def __init__(self, arbalet, diminution=1):
        super(RPiLink, self).__init__(arbalet, diminution)
        self.arbalet = arbalet
        self._connected = False
        self.check_import()
        brightness = min(255, max(1, int(255*diminution)))  # TODO take into account
        self.count = self.arbalet.height * self.arbalet.width
        self.count_spi_bytes = self.count*3
        self.data = np.zeros(self.count_spi_bytes, dtype=np.uint8)
        self.tx = np.zeros(self.count_spi_bytes * 4, dtype=np.uint8)
        self.spi = spidev.SpiDev()
        self.speed = self.arbalet.config["spi"]["speed"]
        self.start()

    def check_import(self):
        # Check import only if this driver has been instanciated
        try:
            cls = spidev
        except NameError as e:
            raise ImportError("No spidev found, make sure you have pulled and installed the git submodule py-spidev")

    def is_connected(self):
        return self._connected

    def connect(self):
        self.spi.open(self.arbalet.config['spi']['bus'], self.arbalet.config['spi']['device'])
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

