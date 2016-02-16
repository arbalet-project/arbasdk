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
from arbasdk.sensors import MODE_OFF, CapacitiveTouch

__all__ = ['Arbalet']

class Arbalet(object):
    def __init__(self, simulation=True, hardware=False, server='', touch_mode=MODE_OFF, diminution=1, factor_sim=30, config='', interactive=True):
        self.simulation = simulation
        self.hardware = hardware
        self.diminution = diminution
        self.server = server
        self.touch = CapacitiveTouch(touch_mode)

        if config=='':
            cfg_path = path.join(path.dirname(sdk_file), '..', 'config', 'default.cfg')
            cfg_parser = RawConfigParser()
            cfg_parser.read(cfg_path)
            config = cfg_parser.get('DEFAULT', 'config')

        if not path.isfile(config):
            config = path.join(path.dirname(sdk_file), '..', 'config', config)
        if not path.isfile(config):
            raise Exception("Config file '{}' not found".format(config))

        with open(config, 'r') as f:
            self.config = load(f)

        self.height = len(self.config['mapping'])
        self.width = len(self.config['mapping'][0]) if self.height>0 else 0
        self.user_model = Arbamodel(self.height, self.width, 'black')
        self.models = [self.user_model]

        if touch_mode is not None:
            self.models.append(self.touch.model)

        if self.simulation:
            self.arbasim = Arbasim(self, self.height*factor_sim, self.width*factor_sim, interactive=interactive)

        if self.hardware:
            self.arbalink = Arbalink(self, self.touch, diminution=self.diminution)

        if len(self.server)>0:
            server = self.server.split(':')
            if len(server)==2:
                self.arbaclient = Arbaclient(self, server[0], int(server[1]))
            elif len(server)==1:
                self.arbaclient = Arbaclient(self, server[0])
            else:
                raise Exception('Incorrect server address, use ip:port or ip')

    @property
    def end_model(self):
        # The final model is the addition of all models of each layer
        return reduce(Arbamodel.__add__, self.models)

    def set_model(self, model):
        if self.simulation:
            self.arbasim.set_model(model if self.touch is None else self.touch.model + model)
        if self.hardware:
            self.arbalink.set_model(model if self.touch is None else self.touch.model + model)
        if len(self.server)>0:
            self.arbaclient.set_model(model if self.touch is None else self.touch.model + model)

    def close(self, reason='unknown'):
        if self.simulation:
            self.arbasim.close(reason)
        if self.hardware:
            self.arbalink.close()
        if len(self.server)>0:
            self.arbaclient.close(reason)
