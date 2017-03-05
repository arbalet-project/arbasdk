from ..tools import Rate
from time import time
from numpy import zeros


class Flash(object):
    """
    Make a model flashing at a specific rate
    Operates directly in the internal numpy representation to keep the references intact
    """
    def __init__(self, model):
        self.model = model
        self.models = [zeros((self.model.height, self.model.width, 3)), self.model._model]

    def flash(self, duration=4., speed=1.5):
        """
        Blocking call flashing the current model on and off (mainly for game over)
        :param duration: Approximate duration of flashing in seconds
        :param rate: Rate of flashing in Hz
        """
        rate = Rate(speed)
        t0 = time()
        model_id = 0

        model_off = False
        while time() - t0 < duration or model_off:
            with self.model:
                self.model._model = self.models[model_id]
            model_id = (model_id + 1) % 2
            model_off = not model_off
            rate.sleep()