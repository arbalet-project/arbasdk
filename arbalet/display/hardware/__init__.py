from os.path import realpath as _realpath
from .simulator import Simulator

def get_hardware_link(host, hardware_config, stop_event=None):
    if hardware_config["controller"] in ["arduino"]:
        from .arduino import ArduinoDisplayServer as _ArduinoLink
        return _ArduinoLink(host, hardware_config, stop_event=stop_event)
    if hardware_config["controller"] in ["rpi_spi", "raspberrypi", "pi", 'spi"']:
        from .raspberrypi import RPiSPIDisplayServer as _RPiLinkSPI
        return _RPiLinkSPI(host, hardware_config, stop_event=stop_event)
    if hardware_config["controller"] in ["rpi_pwm", "pwm"]:
        from .raspberrypi import RPiPWMDisplayServer as _RPiLinkPWM
        return _RPiLinkPWM(host, hardware_config, stop_event=stop_event)
    raise NotImplementedError("{} knows no implementation of link type \"{}\" specified in config file".format(_realpath(__file__), hardware_config["controller"]))

