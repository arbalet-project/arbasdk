"""
    Arbalet - ARduino-BAsed LEd Table

    This class is the Arbalet master
    Controller calling all other features

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from .arbasim import Simulator
from .arbalink import Arbalink
from .arbaclient import Arbaclient
from .arbamodel import Model
from .events import Events
from .sensors import CapacitiveTouch
from functools import reduce
from os import path
from json import load
from configparser import RawConfigParser
from threading import RLock

__all__ = ['Arbalet']

class Arbalet(object):
    def __init__(self, simulation=True, hardware=False, server='', diminution=1, factor_sim=30, config='', interactive=True, joystick=''):
        if config=='' or joystick=='':
            cfg_path = path.join(path.dirname(__file__), '..', 'config', 'default.cfg')
            cfg_parser = RawConfigParser()
            cfg_parser.read(cfg_path)
            if config=='':
                config = cfg_parser.get('DEFAULT', 'config')
            if joystick=='':
                joystick = cfg_parser.get('DEFAULT', 'joystick')

        if not path.isfile(config):
            config = path.join(path.dirname(__file__), '..', 'config', config)
        if not path.isfile(config):
            raise IOError("Config file '{}' not found".format(config))

        if not path.isfile(joystick):
            joystick = path.join(path.dirname(__file__), '..', 'config', joystick)
        if not path.isfile(joystick):
            raise IOError("Joystick mapping file '{}' not found".format(joystick))

        try:
            with open(config, 'r') as f:
                self.config = load(f)
        except ValueError as e:
            raise ValueError("Your configuration file {} has an incorrect format, make sure it is a valid JSON. {}".format(config, str(e)))
        except IOError as e:
            raise IOError("Configuration file {} can't be read. {}".format(config, str(e)))

        try:
            with open(joystick, 'r') as f:
                self.joystick = load(f)
        except ValueError as e:
            raise ValueError("Your joystick mapping file {} has an incorrect format, make sure it is a valid JSON. {}".format(joystick, str(e)))
        except IOError as e:
            raise IOError("Joystick mapping file {} can't be read. {}".format(joystick, str(e)))

        self._simulation = simulation
        self._hardware = hardware
        self._server = server

        self.diminution = diminution
        self.height = len(self.config['mapping'])
        self.width = len(self.config['mapping'][0]) if self.height>0 else 0
        self.user_model = Model(self.height, self.width, 'black')
        self.touch = CapacitiveTouch(config, self.height, self.width)
        self.sdl_lock = RLock()  # Temporary hack to lock pygame calls using SDL before we create a centralized event manager for joystick and so on

        self.events = Events(self, True)

        self._models = {'user': self.user_model,
                        'touch': self.touch.model}

        # Start connection to real, simulated, or network LED table
        self.arbasim = None
        self.arbalink = None
        self.arbaclient = None

        if self._simulation:
            self.arbasim = Simulator(self, self.height*factor_sim, self.width*factor_sim)

        if self._hardware:
            self.arbalink = Arbalink(self, self.diminution)

        if len(self._server)>0:
            server = self._server.split(':')
            if len(server)==2:
                self.arbaclient = Arbaclient(self, server[0], int(server[1]))
            elif len(server)==1:
                self.arbaclient = Arbaclient(self, server[0])
            else:
                raise ValueError('Incorrect server address, use ip:port or ip')

    @property
    def end_model(self):
        # The final model is the addition of all models of each layer
        with self._models['user']:
            with self._models['touch']:
                return self._models['user'] + self._models['touch']

    def close(self, reason='unknown'):
        if self._simulation:
            self.arbasim.close()
        if self._hardware:
            self.arbalink.close()
        if len(self._server)>0:
            self.arbaclient.close()
        self.events.close()
