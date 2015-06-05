"""
    Arbalet - ARduino-BAsed LEd Table
    Arbapp - Arbalet Application

    All Application for Arbalet should inherit from this class.
    Wanna create an awesome Arbalet application? Start here.

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from Arbalet import Arbalet
from Arbamodel import Arbamodel
from pygame import init as pygame_init
import argparse, __builtin__

__all__ = ['Arbapp']

class Arbapp(object):
    app_declared = False  # True when an Arbapp has been instanciated

    def __init__(self, argparser=None, moke_execution=False):
        if Arbapp.app_declared:
            raise RuntimeError('Arbapp can be instanciated only once')

        Arbapp.app_declared = True
        pygame_init()
        self.read_args(argparser)

        self.arbalet = Arbalet(not moke_execution and not self.args.no_gui, not moke_execution and self.args.hardware,
                               self.args.server, self.args.brightness, self.args.factor_sim, self.args.config, interactive=False)

        self.width = self.arbalet.width
        self.height = self.arbalet.height

        self.model = Arbamodel(self.height, self.width, 'black')
        self.set_model(self.model)

    def is_interactive(self):
        """
        :return: True if the code is running interactively with IPYTHON, False otherwise
        """
        return '__IPYTHON__' in vars(__builtin__)

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
                            const='127.0.0.1',
                            default='',
                            help='Address and port of the Arbaserver sharing hardware (ex: myserver.local:33400, 192.168.0.15, ...)')
        parser.add_argument('-c', '--config',
                            type=str,
                            default='',
                            help='Name of the config file describing the table (.json file), if missing the default config in arbasdk/default.cfg will be selected')
        parser.add_argument('-b', '--brightness',
                            type=float,
                            default=1,
                            help='Brightness, intensity of hardware LEDs between 0.0 (all LEDs off) and 1.0 (all LEDs at full brightness)')
        parser.add_argument('-f', '--factor_sim',
                            type=int,
                            default=40,
                            help='Size of the simulated pixels')

        # We parse args normally if running in non-interactive mode, otherwise we ignore args to avoid conflicts with ipython
        self.args = parser.parse_args([] if self.is_interactive() else None)

    def set_model(self, model):
        self.arbalet.set_model(model)

    def run(self):
        raise NotImplementedError("Arbapp.run() must be overidden")

    def start(self):
        try:
            self.run()
        except:
            self.close("Program raised exception")
            raise
        else:
            self.close("Program naturally ended")

    def close(self, reason='unknown'):
        self.arbalet.close(reason)
