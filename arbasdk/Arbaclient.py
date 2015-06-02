"""
    Arbalet - ARduino-BAsed LEd Table

    Arbalet client
    Client for controlling Arbalet over the network

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

import zmq
from threading import Thread
from time import sleep

__all__ = ['Arbaclient']

class Arbaclient(Thread):
    def __init__(self, server='127.0.0.1', port=33400, rate=30, autorun=True):
        Thread.__init__(self)
        self.setDaemon(True)
        self.server = server
        self.port = str(port)
        self.model = None
        self.running = True
        self.rate = rate

        # Network-related attributes
        self.context = zmq.Context()
        self.sender = None

        if autorun:
            self.start()

    def connect(self):
        if not self.sender:
            self.sender = self.context.socket(zmq.PUB)
            self.sender.connect("tcp://{}:{}".format(self.server, self.port))

    def send_model(self):
        if self.model:
            self.sender.send_json(self.model.to_json())

    def set_model(self, model):
        self.model = model

    def close(self, reason='unknown'):
        self.running = False

    def run(self):
        self.connect()
        while self.running:
            self.send_model()
            sleep(1./self.rate)
        self.sender.close()