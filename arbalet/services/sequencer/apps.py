from multiprocessing import Process
from signal import SIGINT
from . import __file__
from os import kill


def get(name):
    """
    Method telling the sequencer what are the app to load depending on their name
    Every JSON entry in the sequence file must have a mapping here
    :param name: Name of the app in the JSON sequence
    :return: a subclass of arbalet.application.Application corresponding to the requested app, or None if app not found
    """
    if name == 'tetris':
        from arbalet.apps.tetris import Tetris
        return Tetris
    elif name == 'snake':
        from arbalet.apps.snake import Snake
        return Snake
    elif name == 'snake.ai':
        from arbalet.apps.snake.ai import SnakeAI
        return SnakeAI
    elif name == 'colors':
        from arbalet.apps.colors import ColorDemo
        return ColorDemo
    elif name == 'lightshero':
        from arbalet.apps.lightshero import LightsHero
        return LightsHero
    elif name == 'spectrum':
        from arbalet.apps.spectrum import SpectrumAnalyser
        return SpectrumAnalyser
    elif name == 'timeclock':
        from arbalet.apps.timeclock import TimeClockApp
        return TimeClockApp
    elif name == 'lost_in_space':
        from arbalet.apps.lost_in_space import LostInSpace
        return LostInSpace
    elif name == 'pixeliser':
        from arbalet.apps.pixeliser import Pixeliser
        return Pixeliser
    elif name == 'images':
        from arbalet.apps.images import ImageReader
        return ImageReader
    elif name == 'bounces':
        from arbalet.apps.bounces import Bounces
        return Bounces
    else:
        print(
        "[Arbalet Sequencer] App '{}' undeclared in the app manager, please declare it in {}".format(name, __file__))
        return None


class AppManager(object):
    """
    Instantiate and load apps
    Compatible with pre-loading
    Pre-loading disabled because incompatible with network sockets :(
    """
    def __init__(self):
        self.apps = {}

    def load(self, name, kwargs={}):
        if name not in self.apps or self.apps[name] is None:
            constructor = get(name)
            if constructor is None:
                return False
            else:
                self.apps[name] = {'object': constructor, # constructor(**kwargs),    # Pre-loading constructor
                                   'args': kwargs,
                                   'process': None}
                return True
        else:
            return True

    def run(self, name, kwargs={}):
        if name not in self.apps or self.apps[name] is None:
            if self.load(name, kwargs) == False:
                return False
        #self.apps[name]['process'] = Process(target=self.apps[name]['process'].start)     # Pre-loaded constructor
        self.apps[name]['process'] = Process(target=lambda :self.apps[name]['object'](**self.apps[name]['args']).start())
        self.apps[name]['process'].start()
        return True

    def is_running(self, name):
        if name not in self.apps:
            return False
        return self.apps[name]['process'].is_alive()

    def stop(self, name):
        if name not in self.apps:
            return False
        if self.apps[name]['process'].is_alive():
            kill(self.apps[name]['process'].pid, SIGINT)
        self.apps[name]['process'].join()
        self.apps[name]['object'] = None
        self.apps[name] = None
        return True
