"""
    Arbalet - ARduino-BAsed LEd Table
    Application - Arbalet Application

    All Application for Arbalet should inherit from this class.
    Wanna create an awesome Arbalet application? Start here.

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from ..config import get_config_parser, ConfigReader
from ..display import DisplayClient, get_display_parser
from ..events import EventClient
from . import Model
import argparse

__all__ = ['Application']

class Application(object):
    app_declared = False  # True when an Application has been instanciated

    def __init__(self, argparser=None, touch_mode='off'):
        if Application.app_declared:
            raise RuntimeError('Application can be instanciated only once')

        Application.app_declared = True
        self.read_args(argparser)
        self.events = EventClient(host=self.args.server)
        self._servers = Servers(self.args)
        self._config = ConfigReader()
        self.width = self._config.hardware['width']
        self.height = self._config.hardware['height']
        self.model = Model(self.height, self.width)
        self._client = DisplayClient(self.model, self.args.server)

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
        parser.add_argument('-o', '--standalone',
                            action='store_const',
                            const=True,
                            default=False,
                            help='Run this app in standalone mode by also starting all background servers')

        parser = get_config_parser(parser)
        parser = get_display_parser(parser)

        # We parse args normally if running in non-interactive mode, otherwise we ignore args to avoid conflicts with ipython
        self.args = parser.parse_args([] if self.is_interactive() else None)


    def run(self):
        raise NotImplementedError("Application.run() must be overidden")

    def start(self):
        try:
            if self.args.standalone:
                self._servers.start()
            self.run()
        finally:
            self.close()
            if self.args.standalone:
                self._servers.stop()

    def close(self):
        self._client.close()


class Servers(object):
    """
    Background servers to run the app in standalone mode
    """
    def __init__(self, args):
        self.processes = []
        self.args = args

    def start(self):
        from subprocess import Popen
        from sys import executable

        self.processes.append(Popen("{} -m arbalet.dbus.proxy".format(executable).strip().split()))
        self.processes.append(Popen("{} -m arbalet.events.server".format(executable).strip().split()))
        hardware = "--hardware" if self.args.hardware else ""
        no_gui = "--no-gui" if self.args.no_gui else ""
        display_params = " ".join(filter(None, [hardware, no_gui]))
        self.processes.append(Popen("{} -m arbalet.display.server {}".format(executable, display_params).strip().split(' ')))

    def stop(self):
        from signal import SIGINT

        for process in self.processes:
            process.send_signal(SIGINT)
        print("[Standalone run] Waiting for servers to shutdown")
        for process in self.processes:
            process.wait()