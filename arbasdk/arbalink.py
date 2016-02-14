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
from copy import deepcopy
from . rate import Rate
from os import name
from arbasdk.events import create_event

__all__ = ['Arbalink']

class Arbalink(Thread):
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

        if name=='nt':  # reserved names: 'posix', 'nt', 'os2', 'ce', 'java', 'riscos'
            self.platform = 'windows'
        else:
            self.platform = 'unix'

        if autorun:
            self.start()

    def connect(self):
        success = False
        device = self.config['devices'][self.platform][self.current_device]
        try:
            self.serial = Serial(device, self.config['speed'], timeout=0)
        except Exception, e:
            print >> stderr, "[Arbalink] Connection to {} at speed {} failed: {}".format(device, self.config['speed'], e.message)
            self.serial = None
            self.current_device = (self.current_device+1) % len(self.config['devices'])
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

    def set_model(self, arbamodel):
        self.model = arbamodel

    def close(self, reason='unknown'):
        self.running = False
        if self.serial:
            self.serial.close()
            self.serial = None

    def run(self):
        def __limit(v):
            return int(max(0, min(255, v)))

        while(self.running):
            reconnect = True
            if self.serial and self.serial.isOpen():
                if self.model:
                    array = bytearray(' '*(self.model.get_height()*self.model.get_width()*3))
                    with self.model:
                        model = deepcopy(self.model._model)

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
                    try:
                        self.serial.write(array) # Write the whole rgb-matrix
                        touch = self.serial.readline() # Wait Arduino's feedback
                    except:
                        pass
                    else:
                        reconnect = False
                        try:
                            create_event(int(touch))
                        except ValueError:
                            pass
            if reconnect:
                self.connect_forever()
            else:
                self.rate.sleep()
