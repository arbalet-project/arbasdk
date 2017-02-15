"""
    Arbalet - ARduino-BAsed LEd Table
    AbstractMapper - Abstract class defining a control mapper
    A control mapper maps low level events (e.g. "key W") to semantic user controls (e.g. "UP")

    Copyright 2017 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from ...config import ConfigReader

__all__ = ['AbstractMapper']


class AbstractMapper(object):
    def __init__(self):
        self.config_reader = ConfigReader()

    def map(self, raw_event):
        """
        Return 0, 1 or N high level events events (e.g. "DOWN", "LEFT"...) associated to the input raw event (e.g. "key WASD")
        :return: None, an event dictionary {} or a list of events dictionaries
        """
        raise NotImplementedError()

