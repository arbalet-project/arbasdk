from ...config import ConfigReader
from time import time

class MiceMapper(object):
    def __init__(self):
        config_reader = ConfigReader()
        self.config = config_reader.hardware['touch']
        # TODO Check on DBus: touch enabled or off?
        self.mode = 'quadridirectional'

    def map(self, raw_event):
        if self.config['num_keys'] > 0:
            h = raw_event['pixel'][0]
            w = raw_event['pixel'][1]
            pressed = raw_event['pressed']
            for touch_key_id, touch_key in enumerate(self.config['keys']):
                for touch_pixel in touch_key:
                    if touch_pixel[0] == h and touch_pixel[1] == w:
                        if self.config['mapping']['quadridirectional'] != "none":
                            event = {'key': self.config['mapping']['quadridirectional'][touch_key_id],
                                     'device': {'type': 'touch', 'id': 'simulated'},
                                     'player': 0,
                                     'pressed': pressed,
                                     'time': time()}
                            return event
            #print('Unknown clicked pixel {}, {} for touch simulation'.format(h, w))
            # No matching can be found if the mouse has moved (especially if refresh rate is low)
            return None
