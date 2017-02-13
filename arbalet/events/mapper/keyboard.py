from ...config import ConfigReader
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT
from time import time

class KeyboardMapper(object):
    def __init__(self):
        config_reader = ConfigReader()
        self.config = config_reader.hardware['touch']
        self.mapping = {K_UP: 'up', K_DOWN:'down', K_RIGHT:'right', K_LEFT:'left'}

    def map(self, raw_event):
        if raw_event['key'] in self.mapping:
            event = {'key': self.mapping[raw_event['key']],
                     'device': {'type': 'keyboard', 'id': 'main'},
                     'player': 0,
                     'pressed': raw_event['pressed'],
                     'time': time()}
            return event
        else:
            return None