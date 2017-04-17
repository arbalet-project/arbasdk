"""
    Arbalet - ARduino-BAsed LEd Table
    Application - Arbalet Application

    All Application for Arbalet should inherit from this class.
    Wanna create an awesome Arbalet application? Start here.

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from .config import get_config_parser, ConfigReader
from .display import DisplayClient, get_user_display_parser
from .events import EventClient
from .core.model import Model
from .core.servers import Servers
from argparse import ArgumentParser


__all__ = ['Application', 'get_application_parser']

def get_application_parser(parser=None):
    if parser is None:
        parser = ArgumentParser(description='This script runs on Arbalet and allows the following arguments:')

    parser.add_argument('-s', '--server',
                        type=str,
                        nargs='?',
                        const=True,
                        default='localhost',
                        help='IP or hostname of the D-Bus, Display and Event servers (ex: myserver.local, 192.168.0.15, ...)'
                             'Do not provide port, it is specified in the D-Bus configuration file')

    parser.add_argument('-b', '--brightness',
                        type=float,
                        default=1,
                        help='Brightness, intensity of hardware LEDs between 0.0 (all LEDs off) and 1.0 (all LEDs at full brightness)')

    parser.add_argument('-nt', '--no-touch',
                        action='store_const',
                        const=True,
                        default=False,
                        help='Disable the touch feature. This option has no influence on apps that are not touch-compatible')

    parser.add_argument('-o', '--standalone',
                        action='store_true',
                        help='Run this app in standalone mode by also starting all background servers')

    parser = get_config_parser(parser)
    parser = get_user_display_parser(parser)
    return parser


class Application(object):
    def __init__(self, host='127.0.0.1', hardware=False, simulation=True, standalone=False, touch_mode='off', **kwargs):
        self.events = EventClient(host=host)
        self._servers = Servers(hardware, simulation)
        self._config = ConfigReader()
        self._standalone = standalone
        self.width = self._config.hardware['width']
        self.height = self._config.hardware['height']
        self.model = Model(self.height, self.width)
        self._client = DisplayClient(self.model, host)

    def run(self):
        raise NotImplementedError("Application.run() must be overidden")

    def start(self):
        try:
            if self._standalone:
                self._servers.start()
            self.run()
        except KeyboardInterrupt:
            if self._standalone:
                self._servers.stop(is_keyboard_interrupt=True)
        else:
            self._servers.stop(is_keyboard_interrupt=False)
        finally:
            self.close()

    def close(self):
        self._client.close()
