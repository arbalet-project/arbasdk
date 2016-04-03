from pygame import init, quit, event, joystick, JOYBUTTONDOWN
from threading import RLock, Thread
from copy import copy
from . rate import Rate

class Events(Thread):
    """
    Arbalet Events manager, also in charge of pygame init and quit
    """

    EVENT_NUM_LIMIT = 1000
    def __init__(self, arbalet, runtime_control):
        """
        Simple event manager duplicating the pygame events for the system (runtime hardware management) and the user (game control)
        The get() method and the system-reserved _get() both poll the pygame event list to keep the list up-to-date and also avoid the pygame internal queue to be full
        TODO: events pygame/touch to be merged into a unique format
        :param enable_system_events: enable the acquisition of system events, must be False if no Arbalink polls the system event queue
        :return:
        """
        Thread.__init__(self)
        self.setDaemon(True)
        self._system_events = []
        self._user_events = []
        self._user_events_lock = RLock()
        self._arbalet = arbalet
        self._rate = Rate(self._arbalet.config['refresh_rate'])
        self._runtime_control = runtime_control
        self.running = False

        # All joysticks are enabled by default
        with self._arbalet.sdl_lock:
            init()
            joystick.init()
            for j in range(joystick.get_count()):
                joy = joystick.Joystick(j)
                joy.init()

        self.start()

    def _get_pygame_events(self):
        with self._arbalet.sdl_lock:
            events = event.get()
        self._system_events = self._system_events + events

        with self._user_events_lock:
            if len(self._user_events) < self.EVENT_NUM_LIMIT:
                # TODO drop the oldest events instead of droping the last ones?
                self._user_events = self._user_events + events

    def get(self):
        """
        Get a copy of events dedicated to the user
        The list of user events has a limit to avoid swamping the memory with unread events
        :return:
        """
        self._get_pygame_events()
        with self._user_events_lock:
            returned_copy = copy(self._user_events)
        self._user_events = []
        return returned_copy

    def _get(self):
        """
        Get a copy of events dedicated to the system
        This method is not to be called by the user, only by the system
        :return: the list of events
        """
        self._get_pygame_events()
        returned_copy = copy(self._system_events)
        self._system_events = []
        return returned_copy

    def close(self):
        self.running = False

    def run(self):
        """
        Run the event manager that redistributes duplicated events to user and SDK, and TODO gathers all events
        """
        self.running = True
        while self.running:
            system_events = self._get()  # Get the system event list
            if self._runtime_control:
                # Check for the touch toggling signal
                for ev in system_events:
                    if ev.type == JOYBUTTONDOWN and ev.button in [4, 6]:
                        self._arbalet.touch.toggle_touch()
                        break
            self._rate.sleep()
        with self._arbalet.sdl_lock:
            quit()