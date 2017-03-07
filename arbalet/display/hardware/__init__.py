from .arduino import ArduinoLink as _ArduinoLink
from .raspberrypi import RPiLinkSPI as _RPiLinkSPI
from .raspberrypi import RPiLinkPWM as _RPiLinkPWM
from os.path import realpath as _realpath
from .simulator import Simulator

def get_hardware_link(layers, hardware_config):
    if hardware_config["controller"] in ["arduino"]: return _ArduinoLink(layers, hardware_config)
    if hardware_config["controller"] in ["rpi_spi", "raspberrypi", "pi", 'spi"']: return _RPiLinkSPI(layers, hardware_config)
    if hardware_config["controller"] in ["rpi_pwm", "pwm"]: return _RPiLinkPWM(layers, hardware_config)
    raise NotImplementedError("{} knows no implementation of link type \"{}\" specified in config file".format(_realpath(__file__), hardware_config["controller"]))

