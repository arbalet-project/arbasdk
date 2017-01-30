"""
    Arbalet - ARduino-BAsed LEd Table

    Arbalet client
    Client for controlling Arbalet over the network

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from threading import Thread
from .rate import Rate
from .dbus import DBusClient

__all__ = ['Arbaclient']

class Arbaclient(Thread):
    def __init__(self, arbalet, host='127.0.0.1'):
        Thread.__init__(self)
        self.setDaemon(True)
        self.server = server
        self.port = str(port)
        self.running = True
        self.rate = Rate(arbalet.config["refresh_rate"])
        self.arbalet = arbalet

        self.bus = DBusClient(host, display_publisher=True)
        self.start()

    def send_model(self):
        self.bus.display.publish(self.arbalet.end_model.to_json())

    def close(self):
        self.running = False

    def run(self):
        while self.running:
            self.send_model()
            self.rate.sleep()
        self.bus.close()
