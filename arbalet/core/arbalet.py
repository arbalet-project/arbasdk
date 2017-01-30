"""
    Arbalet - ARduino-BAsed LEd Table

    This class is the Arbalet master
    Controller calling all other features

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from .arbasim import Simulator
from .link import Arbalink
from .arbaclient import Arbaclient
from .arbamodel import Model
from ..config import ConfigReader

__all__ = ['Arbalet']


class Arbalet(object):
    def __init__(self, simulation=True, hardware=False, server='', diminution=1, factor_sim=30, config='', interactive=True, joystick=''):
        config_reader = ConfigReader(config, joystick)
        self.config = config_reader.hardware
        self.joystick = config_reader.joystick

        self._simulation = simulation
        self._hardware = hardware
        self._server = server

        self.diminution = diminution
        self.height = len(self.config['mapping'])
        self.width = len(self.config['mapping'][0]) if self.height>0 else 0
        self.user_model = Model(self.height, self.width, 'black')

        self._models = {'user': self.user_model}

        # Start connection to real, simulated, or network LED table
        self.arbasim = None
        self.arbalink = None
        self.arbaclient = None

        if self._simulation:
            self.arbasim = Simulator(self, self.height*factor_sim, self.width*factor_sim)

        if self._hardware:
            self.arbalink = Arbalink.factory(self)

        if len(self._server)>0:
            self.arbaclient = Arbaclient(self, server)


    @property
    def end_model(self):
        return self._models['user']

    def handle_mouse_event(self, event):
        if self._simulation:
            self.arbasim.simulate_touch_event(event)

    def close(self):
        if self._simulation:
            self.arbasim.close()
        if self._hardware:
            self.arbalink.close()
        if len(self._server)>0:
            self.arbaclient.close()
