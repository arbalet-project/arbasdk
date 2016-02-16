"""
    Arbalet - ARduino-BAsed LEd Table
    Arbalink - Arbalet Link to the hardware table

    Handle the connection to Arduino

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from threading import Thread
from serial import Serial
from sys import stderr
from time import sleep
from . rate import Rate
from os import name

__all__ = ['Arbalink']

class Arbalink(Thread):
    def __init__(self, arbalet, touch=None, diminution=1, autorun=True):
        Thread.__init__(self)
        self.setDaemon(True)
        self._current_device = 0
        self._serial = None
        self._model = None
        self._diminution = diminution
        self._running = True
        self._arbalet = arbalet
        self._touch = touch
        self._rate = Rate(self._arbalet.config['refresh_rate'])

        if name=='nt':  # reserved names: 'posix', 'nt', 'os2', 'ce', 'java', 'riscos'
            self._platform = 'windows'
        else:
            self._platform = 'unix'

        if autorun:
            self.start()

    def connect(self):
        success = False
        device = self._arbalet.config['devices'][self._platform][self._current_device]
        try:
            self._serial = Serial(device, self._arbalet.config['speed'], timeout=0)
        except Exception, e:
            print >> stderr, "[Arbalink] Connection to {} at speed {} failed: {}".format(device, self._arbalet.config['speed'], e.message)
            self._serial = None
            self._current_device = (self._current_device+1) % len(self._arbalet.config['devices'])
        else:
            success = True
        return success

    def connect_forever(self):
        success = False
        while not success:
            success = self.connect()
            if success:
                break
            sleep(0.05)
        return success

    def close(self, reason='unknown'):
        self._running = False
        if self._serial:
            self._serial.close()
            self._serial = None

    def run(self):
        def __limit(v):
            return int(max(0, min(255, v)))

        while(self._running):
            reconnect = True
            if self._serial and self._serial.isOpen():
                model = self._arbalet.end_model
                array = bytearray(' '*(model.get_height()*model.get_width()*3))

                for h in range(model.get_height()):
                    for w in range(model.get_width()):
                        try:
                            idx = self._arbalet.config['mapping'][h][w]*3 # = mapping shift by 3 colors
                        except IndexError, e:
                            self.close('config error')
                            raise Exception('Incorrect mapping, please check your configuration file, arbalink exiting...')
                        else:
                            pixel = model._model[h][w]
                            array[idx] = __limit(pixel.r*self._diminution)
                            array[idx+1] = __limit(pixel.g*self._diminution)
                            array[idx+2] = __limit(pixel.b*self._diminution)
                try:
                    self._serial.write(array) # Write the whole rgb-matrix
                    touch = self._serial.readline() # Wait Arduino's feedback
                except:
                    pass
                else:
                    reconnect = False
                    if self._touch is not None:
                        try:
                            touch = int(touch)
                        except ValueError:
                            pass
                        else:
                            self._touch.create_event(touch)
            if reconnect:
                self.connect_forever()
            else:
                self._rate.sleep()
