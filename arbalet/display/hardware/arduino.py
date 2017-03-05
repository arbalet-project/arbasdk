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
    
    def __init__(self, layers, hardware_config, diminution=1):
        super(ArduinoLink, self).__init__(layers, hardware_config, diminution)
        self._current_device = 0
        self._serial = None
        self._diminution = diminution
        self._connected = False
        self._previous_touch_int = -1
        self._touch_int = -2
        self.keys = []

        if name=='nt':  # reserved names: 'posix', 'nt', 'os2', 'ce', 'java', 'riscos'
            self._platform = 'windows'
        else:
            self._platform = 'unix'

        self.start()

    def connect(self):
        if self._serial:
            self._serial.close()
        device = self._config['devices'][self._platform][self._current_device]
        try:
            self._serial = Serial(device, self._config['speed'], timeout=3)
        except SerialException as e:
            print("[Arbalink] Connection to {} at speed {} failed: {}".format(device, self._config['speed'], str(e)), file=stderr)
            self._serial = None
            self._current_device = (self._current_device+1) % len(self._config['devices'])
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
            assert version != self.CMD_HELLO, "[Arbalet Arduino link] Hardware has reset unexpectedly during handshake, check wiring and configuration file"
            assert version == self.PROTOCOL_VERSION, "[Arbalet Arduino link] Hardware uses protocol v{}, SDK uses protocol v{}".format(version, self.PROTOCOL_VERSION)
            self.write_short(self._config['height']*self._config['width'])
            self.write_uint8(self._config['leds_pin_number'])
            self.write_uint8(self._config['touch']['num_keys'])
            init_result = self.read_char()
            if init_result == self.CMD_CLIENT_INIT_SUCCESS:
                print("[Arbalet Arduino link] Hardware initialization successful")
                self._connected = True
                return True
            elif init_result == self.CMD_CLIENT_INIT_FAILURE:
                raise ValueError("[Arbalet Arduino link] Arduino can't allocate memory, init failure")
            else:
                raise ValueError("[Arbalet Arduino link] Expected one command of {}, got {}".format([self.CMD_CLIENT_INIT_SUCCESS, self.CMD_CLIENT_INIT_FAILURE], init_result))
        else:
            print("[Arbalet Arduino link] Expected command {}, got {} ({})".format(self.CMD_HELLO, hello, ord(hello)))

    def get_serial_frame(self, end_model):
        frame = end_model.data_frame
        
        array = bytearray(' '*(end_model.get_height()*end_model.get_width()*3), 'ascii')
        for h in range(end_model.get_height()):
            for w in range(end_model.get_width()):
                idx = self.map_pixel_to_led(h, w)*3 # = mapping shift by 3 colors
                array[idx] = frame[h][w][0]
                array[idx+1] = frame[h][w][1]
                array[idx+2] = frame[h][w][2]
        return array

    def read_touch_frame(self):
        try:
            self._touch_int = self.read_short()
            num_keys = self._config['touch']['num_keys']
            keys = []
            for key in range(num_keys):
                key_state = self.read_short()
                keys.append(key_state)
            self.keys = keys  # Prevent concurrency
        except (IOError, SerialException,) as e:
            self._serial.close()
            self._connected = False

    def get_touch_events(self):
            raw_events = []
            if self._previous_touch_int != self._touch_int:
                raw_event = {'type': 'capacitive_touch', 'touch_int': self._touch_int, 'touch_keys': self.keys}
                raw_events.append(raw_event)
                self._previous_touch_int = self._touch_int
            return raw_events

    def write_led_frame(self, end_model):
        try:
            ready = self.read_char()
            commands = [self.CMD_BUFFER_READY, self.CMD_BUFFER_READY_DATA_FOLLOWS]
            if ready in commands:
                frame = self.get_serial_frame(end_model)
                self._serial.write(frame)
            elif len(ready)>0:
                raise ValueError("[Arbalet Arduino link] Expected one command of {}, got {}".format(commands, ready))
        except (IOError, SerialException, ) as e:
            self._serial.close()
            self._connected = False
        else:
            data_follows = ready == self.CMD_BUFFER_READY_DATA_FOLLOWS
            return data_follows

    def close(self):
        super(ArduinoLink, self).close()
        if self._serial:
            self._serial.close()
            self._serial = None
