"""
    Arbalet - ARduino-BAsed LEd Table

    This class is the Arbalet master
    Controller calling all other features

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from . Arbasim import Arbasim
from . Arbalink import Arbalink
from . Arbaclient import Arbaclient
from os import path
from json import load
from ConfigParser import RawConfigParser
from arbasdk import __file__ as sdk_file

__all__ = ['Arbalet']

class Arbalet(object):
    def __init__(self, simulation=True, hardware=False, server='', diminution=1, factor_sim=30, config='', interactive=True):
        self.simulation = simulation
        self.hardware = hardware
        self.diminution = diminution
        self.server = server

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

        if self.simulation:
            self.arbasim = Arbasim(self.height, self.width, self.height*factor_sim, self.width*factor_sim, interactive=interactive)

        if self.hardware:
            self.arbalink = Arbalink(self.config, diminution=self.diminution)

        if len(self.server)>0:
            server = self.server.split(':')
            if len(server)==2:
                self.arbaclient = Arbaclient(server[0], int(server[1]))
            elif len(server)==1:
                self.arbaclient = Arbaclient(server[0])
            else:
                raise Exception('Incorrect server address, use ip:port or ip')


    def set_model(self, model):
        if self.simulation:
            self.arbasim.set_model(model)
        if self.hardware:
            self.arbalink.set_model(model)
        if len(self.server)>0:
            self.arbaclient.set_model(model)

    def close(self, reason='unknown'):
        if self.simulation:
            self.arbasim.close(reason)
        if self.hardware:
            self.arbalink.close()
        if len(self.server)>0:
            self.arbaclient.close(reason)
