from ...config import ConfigReader
from ...tools import Rate
from ...dbus import DBusClient
from .. import SystemEvents, RawEvents


class EventServer(object):
    """
    Arbalet Events Server
    Initializes the available sensors and publishes them on D-Bus
    """
    def __init__(self, server, verbose=False):
        config_reader = ConfigReader()
        self.server = server
        self.verbose = verbose
        self.config = config_reader.hardware
        self.joystick = config_reader.joystick
        self.sensors = [SystemEvents(),
                        RawEvents()]
        self.rate = Rate(100)
        self.bus = DBusClient(host=self.server, event_publisher=True)


        # Mapping the display rotation, if any
        if self.config['transformed']['num_rotations'] == 1:
            self.mapping = {'up': 'right', 'down': 'left', 'left': 'up', 'right': 'down'}
        elif self.config['transformed']['num_rotations'] == 2:
            self.mapping = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
        elif self.config['transformed']['num_rotations'] == 3:
            self.mapping = {'up': 'left', 'down': 'right', 'left': 'down', 'right': 'up'}
        else:
            self.mapping = {'up': 'up', 'down': 'down', 'left': 'left', 'right': 'right'}


    def apply_rotation(self, event):
        # If the display configuration is rotated, rotate directional events accordingly
        if event['key'] in self.mapping:
            event['key'] = self.mapping[event['key']]
        return event

    def work(self):
        for sensor in self.sensors:
            for event in sensor.get():
                event = self.apply_rotation(event)
                self.bus.events.publish(event)
                if self.verbose:
                    print("[Arbalet Event Server DEBUG] {}".format(event))

    def run(self):
        while True:
            try:
                self.work()
                self.rate.sleep()
            except KeyboardInterrupt:
                break
        print("[Arbalet Event server] Shutdown initiated, closing...")
        self.bus.close()

