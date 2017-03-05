"""
    Arbalet - ARduino-BAsed LEd Table

    This class is the Arbalet master
    Controller calling all other features

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from .arbamodel import Model
from ..config import ConfigReader
from ..display import DisplayClient


__all__ = ['Arbalet']


class Arbalet(object):
    def __init__(self, host='127.0.0.1', config='', joystick=''):
        config_reader = ConfigReader(config, joystick)
        self.config = config_reader.hardware
        self.joystick = config_reader.joystick

        self.height = len(self.config['mapping'])
        self.width = len(self.config['mapping'][0]) if self.height>0 else 0

        self._client = DisplayClient(self, host)

    def close(self):
        self._client.close()
