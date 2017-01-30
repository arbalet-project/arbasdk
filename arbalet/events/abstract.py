"""
    Arbalet - ARduino-BAsed LEd Table
    AbstractEvents - Abstract Event Generator Interface
    All devices producing events (joysticks, keyboards, ...) must inherit from it to be compatible with the event manager

    Copyright 2017 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from ..core.config import ConfigReader
__all__ = ['AbstractEvents']

class AbstractEvents(object):
    def __init__(self):
        self.config_reader = ConfigReader()

    def get(self):
        """
        Entry points of apps to get the touch events mapped according to current touch mode
        :return: list of events (dictionary)
        """
        raise NotImplementedError()

