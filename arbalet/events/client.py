"""
    Arbalet - ARduino-BAsed LEd Table
    EventClient -Client to be used by Arbalet apps to read user inputs
    Such as joysticks, keyboards...

    Copyright 2017 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from ..dbus import DBusClient

__all__ = ['EventClient']


class EventClient():
    def __init__(self, host='127.0.0.1'):
        self.bus = DBusClient(host=host, event_subscriber=True)

    def get(self):
        """
        Entry points of apps to get the touch events mapped according to current touch mode
        :return: list of events (dictionary)
        """
        events = []
        while True:
            event = self.bus.events.recv(blocking=False)
            if event is None:
                return events
            else:
                events.append(event)
