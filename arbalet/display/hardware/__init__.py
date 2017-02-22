from .arduino import ArduinoLink as _ArduinoLink
from .raspberrypi import RPiLink as _RPiLink
from os.path import realpath as _realpath
from .simulator import Simulator

def get_hardware_link(arbalet):
    if arbalet.config["controller"] in ["arduino"]: return _ArduinoLink(arbalet)
    if arbalet.config["controller"] in ["rpi", "raspberrypi", "pi"]: return _RPiLink(arbalet)
    raise NotImplementedError("{} knows no implementation of link type \"{}\" specified in config file".format(_realpath(__file__), arbalet.config["controller"]))

