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

    def work(self):
        for sensor in self.sensors:
            for event in sensor.get():
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

