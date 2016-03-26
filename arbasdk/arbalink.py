"""
    Arbalet - ARduino-BAsed LEd Table
    Arbalink - Arbalet Link to the hardware table

    Handle the connection to Arduino

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from threading import Thread
from serial import Serial, SerialException
from struct import pack, unpack
from sys import stderr
from time import sleep, time
from copy import deepcopy
from . rate import Rate
from os import name

__all__ = ['Arbalink']

class Arbalink(Thread):
    CMD_HELLO = 'H'
    CMD_BUFFER_READY = 'B'
    CMD_CLIENT_INIT_SUCCESS = 'S'
    CMD_CLIENT_INIT_FAILURE = 'F'
    PROTOCOL_VERSION = 1

    def __init__(self, config, diminution=1, autorun=True):
        Thread.__init__(self)
        self.setDaemon(True)
        self.current_device = 0
        self.serial = None
        self.model = None
        self.diminution = diminution
        self.running = True
        self.config = config
        self.rate = Rate(self.config['refresh_rate'])
        self.connected = False

        if name=='nt':  # reserved names: 'posix', 'nt', 'os2', 'ce', 'java', 'riscos'
            self.platform = 'windows'
        else:
            self.platform = 'unix'

        if autorun:
            self.start()

    def connect(self):
        if self.serial:
            self.serial.close()
        device = self.config['devices'][self.platform][self.current_device]
        try:
            self.serial = Serial(device, self.config['speed'], timeout=15)
        except SerialException, e:
            print >> stderr, "[Arbalink] Connection to {} at speed {} failed: {}".format(device, self.config['speed'], e.message)
            self.serial = None
            self.current_device = (self.current_device+1) % len(self.config['devices'])
            return False
        else:
            try:
                self.handshake()
            except (IOError, SerialException, OSError) as e:
                print >> stderr, "[Arbalink] Handshake failure: {}".format(e.message)
                return False
            return True

    def connect_forever(self):
        success = False
        while not success:
            success = self.connect()
            if success:
                break
            sleep(0.5)
        return success

    def is_connected(self):
        return self.serial is not None and self.serial.isOpen() and self.connected

    def read_uint8(self):
        return ord(self.read_char())

    def write_uint8(self, i):
        self.write_char(chr(i))

    def read_char(self):
        return unpack('<c', self.serial.read())[0]

    def write_char(self, c):
        self.serial.write(pack('<c', c))

    def read_short(self):
        return unpack('<h', self.serial.read(2))

    def write_short(self, s):
        self.serial.write(pack('<h', s))

    def handshake(self):
        self.connected = False
        hello = self.read_char()
        if hello == self.CMD_HELLO:
            self.write_char(self.CMD_HELLO)
            version = self.read_uint8()
            assert version == self.PROTOCOL_VERSION, "Hardware uses protocol v{}, SDK uses protocol v{}".format(version, self.PROTOCOL_VERSION)
            self.write_short(self.model.get_height()*self.model.get_width())
            self.write_uint8(self.config['leds_pin_number'])
            self.write_uint8(0)  # Touch type: No touch feature in this branch
            init_result = self.read_char()
            if init_result == self.CMD_CLIENT_INIT_SUCCESS:
                print "Arbalet hardware initialization successful"
                self.connected = True
                return True
            elif init_result == self.CMD_CLIENT_INIT_FAILURE:
                raise IOError("Arduino can't allocate memory, init failure")
        else:
            raise IOError("Expected command {}, got {} ({})".format(self.CMD_HELLO, hello, ord(hello)))

    def set_model(self, arbamodel):
        self.model = arbamodel

    def close(self, reason='unknown'):
        self.running = False
        if self.serial:
            self.serial.close()
            self.serial = None

    def get_serial_frame(self, model):
        def __limit(v):
            return int(max(0, min(255, v)))

        array = bytearray(' '*(self.model.get_height()*self.model.get_width()*3))
        for h in range(self.model.get_height()):
            for w in range(self.model.get_width()):
                try:
                    idx = self.config['mapping'][h][w]*3 # = mapping shift by 3 colors
                except IndexError, e:
                    self.close('config error')
                    raise Exception('Incorrect mapping, please check your configuration file, arbalink exiting...')
                else:
                    pixel = model[h][w]
                    array[idx] = __limit(pixel.r*self.diminution)
                    array[idx+1] = __limit(pixel.g*self.diminution)
                    array[idx+2] = __limit(pixel.b*self.diminution)
        return array

    def write_serial_frame(self, frame):
        ready = self.serial.read()
        if ready == self.CMD_BUFFER_READY:
            self.serial.write(frame)
        elif len(ready)>0:
            raise IOError("Expected command {}, got {}".format(self.CMD_BUFFER_READY, ready))

    def run(self):
        while(self.running):
            if self.is_connected():
                if self.model:
                    with self.model:
                        model = deepcopy(self.model._model)

                    array = self.get_serial_frame(model)

                    try:
                        self.write_serial_frame(array)
                    except (SerialException, OSError) as e:
                        self.connected = False
                self.rate.sleep()
            else:
                self.connect_forever()
