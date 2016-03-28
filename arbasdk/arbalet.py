"""
    Arbalet - ARduino-BAsed LEd Table

    This class is the Arbalet master
    Controller calling all other features

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from . arbasim import Arbasim
from . arbalink import Arbalink
from . arbaclient import Arbaclient
from os import path
from json import load
from ConfigParser import RawConfigParser
from arbasdk import __file__ as sdk_file
from arbasdk import Arbamodel
from arbasdk.sensors import CapacitiveTouch

__all__ = ['Arbalet']

class Arbalet(object):
    def __init__(self, simulation=True, hardware=False, server='', diminution=1, factor_sim=30, config='', interactive=True):
        if config=='':
            cfg_path = path.join(path.dirname(sdk_file), '..', 'config', 'default.cfg')
            cfg_parser = RawConfigParser()
            cfg_parser.read(cfg_path)
            config = cfg_parser.get('DEFAULT', 'config')

        if not path.isfile(config):
            config = path.join(path.dirname(sdk_file), '..', 'config', config)
        if not path.isfile(config):
            raise Exception("Config file '{}' not found".format(config))

        try:
            with open(config, 'r') as f:
                self.config = load(f)
        except ValueError, e:
            raise ValueError("Your configuration file {} has an incorrect format, make sure it is a valid JSON. {}".format(config, e.message))
        except IOError, e:
            raise IOError("Configuration file {} can't be read. {}".format(config, e.message))

        self.diminution = diminution
        self.height = len(self.config['mapping'])
        self.width = len(self.config['mapping'][0]) if self.height>0 else 0
        self.user_model = Arbamodel(self.height, self.width, 'black')
        self.touch = CapacitiveTouch(config, self.height, self.width)

        self._models = {'user': self.user_model,
                        'touch': self.touch.model}
        self._simulation = simulation
        self._hardware = hardware
        self._server = server

        if self._simulation:
            self.arbasim = Arbasim(self, self.height*factor_sim, self.width*factor_sim, interactive=interactive)

        if self._hardware:
            self.arbalink = Arbalink(self, self.touch, diminution=self.diminution)

        if len(self._server)>0:
            server = self._server.split(':')
            if len(server)==2:
                self.arbaclient = Arbaclient(self, server[0], int(server[1]))
            elif len(server)==1:
                self.arbaclient = Arbaclient(self, server[0])
            else:
                raise Exception('Incorrect server address, use ip:port or ip')

    @property
    def end_model(self):
        # The final model is the addition of all models of each layer
        return reduce(Arbamodel.__add__, self._models.values())

    def close(self, reason='unknown'):
        if self._simulation:
            self.arbasim.close(reason)
        if self._hardware:
            self.arbalink.close()
        if len(self._server)>0:
            self.arbaclient.close(reason)
