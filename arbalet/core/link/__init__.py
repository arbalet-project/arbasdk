from .arduino import ArduinoLink as _ArduinoLink
from .raspberrypi import RPiLink as _RPiLink

from os.path import realpath as _realpath


class Arbalink(object):
    @staticmethod
    def factory(arbalet):
        if arbalet.config["controller"] in ["arduino"]: return _ArduinoLink(arbalet)
        raise NotImplementedError("{} knows no implementation of link type \"{}\"".format(_realpath(__file__), repr(type)))

