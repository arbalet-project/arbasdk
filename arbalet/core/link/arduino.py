"""
    Arbalet - ARduino-BAsed LEd Table
    ArduinoLink - Arbalet Link to the hardware table using Arduino

    Handle the connection to Arduino

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from __future__ import print_function  # py2 stderr
from .abstract import AbstractLink
from serial import Serial, SerialException
from struct import pack, unpack, error
from sys import stderr
from os import name

__all__ = ['ArduinoLink']

class ArduinoLink(AbstractLink):
    CMD_HELLO = b'H'
    CMD_BUFFER_READY = b'B'
    CMD_BUFFER_READY_DATA_FOLLOWS = b'D'
    CMD_CLIENT_INIT_SUCCESS = b'S'
    CMD_CLIENT_INIT_FAILURE = b'F'
    PROTOCOL_VERSION = 2
    
    def __init__(self, arbalet, diminution=1):
        super(ArduinoLink, self).__init__(arbalet, diminution)
        self._current_device = 0
        self._serial = None
        self._diminution = diminution
        self._arbalet = arbalet
        self._connected = False

        if name=='nt':  # reserved names: 'posix', 'nt', 'os2', 'ce', 'java', 'riscos'
            self._platform = 'windows'
        else:
            self._platform = 'unix'

        self.start()

    def connect(self):
        if self._serial:
            self._serial.close()
        device = self._arbalet.config['devices'][self._platform][self._current_device]
        try:
            self._serial = Serial(device, self._arbalet.config['speed'], timeout=3)
        except SerialException as e:
            print("[Arbalink] Connection to {} at speed {} failed: {}".format(device, self._arbalet.config['speed'], str(e)), file=stderr)
            self._serial = None
            self._current_device = (self._current_device+1) % len(self._arbalet.config['devices'])
            return False
        else:
            try:
                self.handshake()
            except (IOError, SerialException, OSError) as e:
                print("[Arbalink] Handshake failure: {}".format(str(e)), file=stderr)
                return False
            return True

    def is_connected(self):
        return self._serial is not None and self._serial.isOpen() and self._connected

    def read_uint8(self):
        return ord(self.read_char())

    def write_uint8(self, i):
        self._serial.write(pack('<B', i))

    def read_char(self):
        try:
            return unpack('<c', self._serial.read())[0]
        except error:
            self._connected = False
            return '\0'

    def write_char(self, c):
        self._serial.write(pack('<c', bytes(c)))

    def read_short(self):
        try:
            return unpack('<H', self._serial.read(2))[0]
        except error:
            self._connected = False
            return 0

    def write_short(self, s):
        self._serial.write(pack('<H', s))

    def handshake(self):
        self._connected = False
        hello = self.read_char()
        if hello == self.CMD_HELLO:
            self.write_char(self.CMD_HELLO)
            version = self.read_uint8()
            assert version != self.CMD_HELLO, "Hardware has reset unexpectedly during handshake, check wiring and configuration file"
            assert version == self.PROTOCOL_VERSION, "Hardware uses protocol v{}, SDK uses protocol v{}".format(version, self.PROTOCOL_VERSION)
            self.write_short(self._arbalet.end_model.get_height()*self._arbalet.end_model.get_width())
            self.write_uint8(self._arbalet.config['leds_pin_number'])
            self.write_uint8(self._arbalet.config['touch']['num_keys'])
            init_result = self.read_char()
            if init_result == self.CMD_CLIENT_INIT_SUCCESS:
                print("Arbalet hardware initialization successful")
                self._connected = True
                return True
            elif init_result == self.CMD_CLIENT_INIT_FAILURE:
                raise IOError("Arduino can't allocate memory, init failure")
            else:
                raise IOError("Expected one command of {}, got {}".format([self.CMD_CLIENT_INIT_SUCCESS, self.CMD_CLIENT_INIT_FAILURE], init_result))
        else:
            raise IOError("Expected command {}, got {} ({})".format(self.CMD_HELLO, hello, ord(hello)))

    def get_serial_frame(self, end_model):
        def __limit(v):
            return int(max(0, min(255, v)))
        
        array = bytearray(' '*(end_model.get_height()*end_model.get_width()*3), 'ascii')
        for h in range(end_model.get_height()):
            for w in range(end_model.get_width()):
                idx = self.map_pixel_to_led(h, w)*3 # = mapping shift by 3 colors
                pixel = end_model._model[h][w]
                array[idx] = __limit(pixel[0]*self._diminution)
                array[idx+1] = __limit(pixel[1]*self._diminution)
                array[idx+2] = __limit(pixel[2]*self._diminution)
        return array

    def read_touch_frame(self):
        touch_int = self.read_short()
        num_keys = self._arbalet.config['touch']['num_keys']
        keys = []
        for key in range(num_keys):
            key_state = self.read_short()
            keys.append(key_state)
        if self._arbalet.touch is not None and self._arbalet.config['touch']['num_keys'] > 0:
            self._arbalet.touch.create_event(touch_int, keys)

    def write_led_frame(self, end_model):
        ready = self.read_char()
        commands = [self.CMD_BUFFER_READY, self.CMD_BUFFER_READY_DATA_FOLLOWS]
        if ready in commands:
            frame = self.get_serial_frame(end_model)
            self._serial.write(frame)
        elif len(ready)>0:
            raise IOError("Expected one command of {}, got {}".format(commands, ready))
        data_follows = ready == self.CMD_BUFFER_READY_DATA_FOLLOWS
        return data_follows

    def close(self):
        super(ArduinoLink, self).close()
        if self._serial:
            self._serial.close()
            self._serial = None
