from ...config import ConfigReader
from .touch import TouchMapper
from time import time

class MiceMapper(TouchMapper):
    def __init__(self):
        super(MiceMapper, self).__init__()
        config_reader = ConfigReader()
        self.config = config_reader.hardware['touch']

    def map(self, raw_event):
        if self.config['num_keys'] > 0:
            h = raw_event['pixel'][0]
            w = raw_event['pixel'][1]
            pressed = raw_event['pressed']
            for touch_key_id, touch_key in enumerate(self.config['keys']):
                for touch_pixel in touch_key:
                    if touch_pixel[0] == h and touch_pixel[1] == w:
                        self._touch_keys_booleans[touch_key_id] = pressed
                        if self.config['mapping']['quadridirectional'] != "none":
                            event = {'key': self.config['mapping']['quadridirectional'][touch_key_id],
                                     'device': {'type': 'touch', 'id': 'simulated'},
                                     'player': 0,
                                     'pressed': pressed,
                                     'time': time()}
                                    # Update the model according to this event
                            self.update_model()
                            return event
            #print('Unknown clicked pixel {}, {} for touch simulation'.format(h, w))
            # No matching can be found if the mouse has moved (especially if refresh rate is low)
            self.update_model()
            return None
