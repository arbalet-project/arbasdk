"""
    Arbalet - ARduino-BAsed LEd Table

    Arbalet Display Server
    Gathers all models and layers from D-Bus, and dispatches them on simulation and hardware
    Copyright 2017 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from ...config import ConfigReader
from ...display.hardware import get_hardware_link, Simulator


class DisplayServer(object):
    def __init__(self, hardware):
        self.hardware = hardware
        config_reader = ConfigReader()
        self.config = config_reader.hardware

    def run(self):
        if self.hardware:
            print("[Arbalet Display Server] starting hardware link")
            get_hardware_link('127.0.0.1', self.config).run()
        else:
            print("[Arbalet Display Server] starting simulation")
            Simulator('127.0.0.1', self.config).run()


