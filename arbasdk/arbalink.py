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
from time import sleep
from . rate import Rate
from os import name

__all__ = ['Arbalink']

class Arbalink(Thread):
    CMD_HELLO = 'H'
    CMD_BUFFER_READY = 'B'
    CMD_CLIENT_INIT_SUCCESS = 'S'
    CMD_CLIENT_INIT_FAILURE = 'F'
    PROTOCOL_VERSION = 1
    
    def __init__(self, arbalet, touch=None, diminution=1, autorun=True):
        Thread.__init__(self)
        self.setDaemon(True)
        self._current_device = 0
        self._serial = None
        self._diminution = diminution
        self._running = True
        self._arbalet = arbalet
        self._touch = touch
        self._rate = Rate(self._arbalet.config['refresh_rate'])
        self._connected = False

        if name=='nt':  # reserved names: 'posix', 'nt', 'os2', 'ce', 'java', 'riscos'
            self._platform = 'windows'
        else:
            self._platform = 'unix'

        if autorun:
            self.start()

    def connect(self):
        if self._serial:
            self._serial.close()
        device = self._arbalet.config['devices'][self._platform][self._current_device]
        try:
            self._serial = Serial(device, self._arbalet.config['speed'], timeout=3)
        except SerialException, e:
            print >> stderr, "[Arbalink] Connection to {} at speed {} failed: {}".format(device, self._arbalet.config['speed'], e.message)
            self._serial = None
            self._current_device = (self._current_device+1) % len(self._arbalet.config['devices'])
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
        return self._serial is not None and self._serial.isOpen() and self._connected

    def read_uint8(self):
        return ord(self.read_char())

    def write_uint8(self, i):
        self.write_char(chr(i))

    def read_char(self):
        return unpack('<c', self._serial.read())[0]

    def write_char(self, c):
        self._serial.write(pack('<c', c))

    def read_short(self):
        return unpack('<h', self._serial.read(2))

    def write_short(self, s):
        self._serial.write(pack('<h', s))

    def handshake(self):
        self._connected = False
        hello = self.read_char()
        if hello == self.CMD_HELLO:
            self.write_char(self.CMD_HELLO)
            version = self.read_uint8()
            assert version == self.PROTOCOL_VERSION, "Hardware uses protocol v{}, SDK uses protocol v{}".format(version, self.PROTOCOL_VERSION)
            self.write_short(self._arbalet.end_model.get_height()*self._arbalet.end_model.get_width())
            self.write_uint8(self._arbalet.config['leds_pin_number'])
            self.write_uint8(0)  # Touch type: No touch feature in this branch
            init_result = self.read_char()
            if init_result == self.CMD_CLIENT_INIT_SUCCESS:
                print "Arbalet hardware initialization successful"
                self._connected = True
                return True
            elif init_result == self.CMD_CLIENT_INIT_FAILURE:
                raise IOError("Arduino can't allocate memory, init failure")
        else:
            raise IOError("Expected command {}, got {} ({})".format(self.CMD_HELLO, hello, ord(hello)))

    def close(self, reason='unknown'):
        self._running = False
        if self._serial:
            self._serial.close()
            self._serial = None

    def get_serial_frame(self):
        def __limit(v):
            return int(max(0, min(255, v)))
        
        end_model = self._arbalet.end_model
        array = bytearray(' '*(end_model.get_height()*end_model.get_width()*3))
        for h in range(end_model.get_height()):
            for w in range(end_model.get_width()):
                try:
                    idx = self._arbalet.config['mapping'][h][w]*3 # = mapping shift by 3 colors
                except IndexError, e:
                    self.close('config error')
                    raise Exception('Incorrect mapping, please check your configuration file, arbalink exiting...')
                else:
                    pixel = end_model._model[h][w]
                    array[idx] = __limit(pixel.r*self._diminution)
                    array[idx+1] = __limit(pixel.g*self._diminution)
                    array[idx+2] = __limit(pixel.b*self._diminution)
        return array

    def write_serial_frame(self, frame):
        ready = self._serial.read()
        if ready == self.CMD_BUFFER_READY:
            self._serial.write(frame)
        elif len(ready)>0:
            raise IOError("Expected command {}, got {}".format(self.CMD_BUFFER_READY, ready))

    def run(self):
        while(self._running):
            if self.is_connected():
                array = self.get_serial_frame()

                try:
                    self.write_serial_frame(array)
                except (SerialException, OSError) as e:
                    self._connected = False
                self._rate.sleep()
            else:
                self.connect_forever()
    
