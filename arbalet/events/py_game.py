from pygame import display, event as pygame_event, joystick
from pygame import JOYBUTTONUP, JOYBUTTONDOWN, K_LEFT, K_RIGHT, K_DOWN, K_UP, JOYHATMOTION, JOYAXISMOTION
from time import time
from .abstract import AbstractEvents


class SystemEvents(AbstractEvents):

    @staticmethod
    def map_hat(prev, out, a, b):
        """
        Map pygame hat events [-1, 0, 1] => 'left', True (= left pressed)
        """
        prev = prev + 1
        out = out + 1
        p = True
        r = False
        matrix = [[[], [[a, r]], [[b, p], [a, r]]],
                  [[[a, p]], [], [[b, p]]],
                  [[[b, r], [a, p]], [[b, r]], []]]
        return matrix[prev][out]

    # Joystick keys mapping
    joy_mapping = {K_LEFT: 'left', K_RIGHT: 'right', K_DOWN: 'down', K_UP: 'up'}

    def __init__(self):
        super(SystemEvents, self).__init__()
        display.init()
        joystick.init()
        self.hats = []
        for j in range(joystick.get_count()):
            joy = joystick.Joystick(j)
            joy.init()
            hats = []
            for hat in range(joy.get_numhats()):
                hats.append([0, 0])
            self.hats.append(hats)

    def get(self):
        """
        Get events event from pygame to dictionaries
        :param event: a pygame.Event object from pygame
        :return: dict of type {'key': 'left', 'device': keyboard', 'pressed': True, 'time': 1485621689.548}
        """
        user_events = []
        for e in pygame_event.get():
            if e.type in [JOYBUTTONUP, JOYBUTTONDOWN]:
                key = self.joy_mapping[e.button] if e.button in self.joy_mapping else e.button

                user_events.append({'key': key,
                                    'device': {'type': 'joystick', 'id': e.joy},
                                    'pressed': e.type == JOYBUTTONDOWN,
                                    'time': time()})

            elif e.type == JOYHATMOTION:
                if len(e.value) != 2:
                    print("pygame system events has received a joystick event with unsupported number of hat directions: {}".format(len(e.value)))
                    continue

                for key, (a, b) in enumerate((('left', 'right'), ('down', 'up'))):
                    new_hat = e.value[key]
                    old_hat = self.hats[e.joy][e.hat][key]
                    events = self.map_hat(old_hat, new_hat, a, b)
                    for event in events:
                        user_events.append({'key': event[0],
                                            'device': {'type': 'joystick', 'id': e.joy},
                                            'player': 0,
                                            'pressed': event[1],
                                            'time': time()})
                        self.hats[e.joy][e.hat][key] = e.value[key]

            elif e.type == JOYAXISMOTION:
                continue

        return user_events

