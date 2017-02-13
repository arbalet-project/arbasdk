from pygame import  K_LEFT, K_RIGHT, K_DOWN, K_UP
from .abstract import AbstractEvents
from ..dbus import DBusClient
from .mapper import MiceMapper
from .mapper import KeyboardMapper
from .mapper import CapacitiveTouchMapper

class RawEvents(AbstractEvents):
    # Joystick keys mapping
    joy_mapping = {K_LEFT: 'left', K_RIGHT: 'right', K_DOWN: 'down', K_UP: 'up'}

    def __init__(self):
        super(RawEvents, self).__init__()
        self.dbus = DBusClient(raw_event_subscriber=True)
        self.mappers = {'mice': MiceMapper(),
                        'kbd': KeyboardMapper(),
                        'capacitive_touch': CapacitiveTouchMapper()}

    def get(self):
        raw_events = []
        while True:
            raw_event = self.dbus.raw_events.recv(blocking=False)
            if raw_event is None:
                break
            raw_events.append(raw_event)

        events =[]
        for e in raw_events:
            if e['type'] not in self.mappers:
                print("[Arbalet Raw Event] Unknown mapper for raw event source '{}'".format(e['type']))
                continue
            mapped_event = self.mappers[e['type']].map(e)
            if mapped_event is not None:
                events.append(mapped_event)
        return events




