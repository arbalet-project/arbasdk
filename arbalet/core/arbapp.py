"""
    Arbalet - ARduino-BAsed LEd Table
    Application - Arbalet Application

    All Application for Arbalet should inherit from this class.
    Wanna create an awesome Arbalet application? Start here.

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from .arbalet import Arbalet
from ..config import get_config_parser
from ..events import EventClient
import argparse

__all__ = ['Application']

class Application(object):
    app_declared = False  # True when an Application has been instanciated

    def __init__(self, argparser=None, moke_execution=False, touch_mode='off'):
        if Application.app_declared:
            raise RuntimeError('Application can be instanciated only once')

        Application.app_declared = True
        self.read_args(argparser)
        self.arbalet = Arbalet(not moke_execution and not self.args.no_gui, not moke_execution and self.args.hardware,
                               self.args.server, self.args.brightness, self.args.factor_sim, self.args.config, interactive=False)
        self.width = self.arbalet.width
        self.height = self.arbalet.height
        self.events = EventClient(host=self.args.server)
        self.init_font(self.model)

    @property
    def model(self):
        return self.arbalet.user_model

    def init_font(self, model):
        try:
            model.set_font(self.arbalet.config['font'], self.arbalet.config['vertical'])
        except KeyError:
            model.set_font()

    def is_interactive(self):
        """
        :return: True if the code is running interactively with IPYTHON, False otherwise
        """
        try:
            __IPYTHON__
        except NameError:
            return False
        else:
            return True

    def read_args(self, argparser):

        if argparser:
            parser = argparser
        else:
            parser = argparse.ArgumentParser(description='This script runs on Arbalet and allows the following arguments:')

        parser.add_argument('-w', '--hardware',
                            action='store_const',
                            const=True,
                            default=False,
                            help='The program must connect directly to Arbalet hardware')
        parser.add_argument('-ng', '--no-gui',
                            action='store_const',
                            const=True,
                            default=False,
                            help='The program must not be simulated on the workstation in a 2D window')
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
        parser.add_argument('-f', '--factor_sim',
                            type=int,
                            default=40,
                            help='Size of the simulated pixels')
        parser.add_argument('-nt', '--no-touch',
                            action='store_const',
                            const=True,
                            default=False,
                            help='Disable the touch feature. This option has no influence on apps that are not touch-compatible')

        parser = get_config_parser(parser)

        # We parse args normally if running in non-interactive mode, otherwise we ignore args to avoid conflicts with ipython
        self.args = parser.parse_args([] if self.is_interactive() else None)


    def run(self):
        raise NotImplementedError("Application.run() must be overidden")

    def start(self):
        try:
            self.run()
        finally:
            self.close()

    def close(self):
        self.arbalet.close()
