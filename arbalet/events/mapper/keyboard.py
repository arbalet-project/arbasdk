from ...config import ConfigReader
from .abstract import AbstractMapper
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_F1, K_F2, K_F3, K_F4, K_F5, K_F6, K_F7, K_F8, K_F9, K_F10, K_SPACE, K_RETURN
from time import time


class KeyboardMapper(AbstractMapper):
    def __init__(self):
        super(KeyboardMapper, self).__init__()
        config_reader = ConfigReader()
        self.config = config_reader.hardware['touch']
        self.mapping = {K_UP: 'up', K_DOWN:'down', K_RIGHT:'right', K_LEFT:'left', K_F1: 'F1', K_F2: 'F2', K_F3: 'F3',
                        K_F4: 'F4', K_F5: 'F5', K_F6: 'F6', K_F7: 'F7', K_F8: 'F8', K_F9: 'F9', K_F10: 'F10',
                        K_RETURN: 'action', K_SPACE: 'action'}

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