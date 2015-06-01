#!/usr/bin/env python3
"""
    Arbalet - ARduino-BAsed LEd Table
    Arbalink - Arbalet Link to the hardware table

    Handle the connection to Arduino

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from threading import Thread, Lock
from serial import Serial
from sys import stderr
from time import sleep, time

__all__ = ['Arbalink']

class Arbalink(Thread):
    def __init__(self, config, diminution=1, autorun=True):
        Thread.__init__(self)
        self.setDaemon(True)
        self.current_device = 0
        self.serial = None
        self.serial_lock = Lock()
        self.model = None
        self.diminution = diminution
        self.running = True
        self.config = config

        if autorun:
            self.start()

    def connect(self):
        success = False
        device = self.config['devices'][self.current_device]
        with self.serial_lock:
            try:
                self.serial = Serial(device, self.config['speed'], timeout=0)
            except Exception, e:
                print >> stderr, "[Arbalink] Connection to {} at speed {} failed: {}".format(device, self.config['speed'], e.message)
                self.serial = None
                self.current_device = (self.current_device+1) % len(self.config['devices'])
            else:
                success = True
        if success:
            sleep(2)
        return success

    def connect_until(self, timeout, num_attempts=20):
        success = False
        start_time = time()
        while not success:
            success = self.connect()
            elapsed_time = time()-start_time
            if not success and elapsed_time<timeout:
                sleep(float(timeout)/num_attempts)
            else:
                break
        return success

    def set_model(self, arbamodel):
        self.model = arbamodel

    def close(self, reason='unknown'):
        self.running = False
        with self.serial_lock:
            if self.serial:
                self.serial.close()
                self.serial = None

    def run(self):
        def __limit(v):
            return int(max(0, min(255, v)))

        while(self.running):
            reconnect = True
            with self.serial_lock:
                if self.serial and self.serial.isOpen():
                    if self.model:
                        array = bytearray(' '*(self.model.get_height()*self.model.get_width()*3))
                        for h in range(self.model.get_height()):
                            for w in range(self.model.get_width()):
                                idx = self.config['mapping'][h][w]*3 # = mapping shift by 3 colors
                                # an IndexError here on bytearray could mean that config file is wrong
                                array[idx] = __limit(self.model.model[h][w].r*self.diminution)
                                array[idx+1] = __limit(self.model.model[h][w].g*self.diminution)
                                array[idx+2] = __limit(self.model.model[h][w].b*self.diminution)
                        try:
                            self.serial.write(array) # Write the whole rgb-matrix
                            #self.serial.readline() # Wait Arduino's feedback
                        except:
                            pass
                        else:
                            reconnect = False
            if reconnect:
                self.connect_until(60)
            else:
                sleep(1./self.config['refresh_rate'])
