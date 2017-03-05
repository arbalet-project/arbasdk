"""
    Arbalet - ARduino-BAsed LEd Table

    Arbalet controller for interactive use in ipython or ipython notebook

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from .model import Model
from .servers import Servers
from ..config import ConfigReader
from ..display import DisplayClient

__all__ = ['InteractiveArbalet']


class InteractiveArbalet(object):
    def __init__(self, host='127.0.0.1', config='', joystick='', hardware=False, simulation=True):
        config_reader = ConfigReader(config, joystick)
        self.config = config_reader.hardware
        self.joystick = config_reader.joystick
        self._no_gui = not simulation
        self._hardware = hardware

        self.height = self.config['height']
        self.width = self.config['width']
        self.model = Model(self.height, self.width)

        if hardware or simulation:
            self._servers = Servers(self._hardware, self._no_gui)
            self._servers.start()
        else:
            self._servers = None

        self._client = DisplayClient(self.model, host)

    def close(self):
        self._client.close()
        if self._servers is not None:
            self._servers.stop()
