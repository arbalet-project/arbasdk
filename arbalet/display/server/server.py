"""
    Arbalet - ARduino-BAsed LEd Table

    Arbalet Display Server
    Gathers all models and layers from D-Bus, and dispatches them on simulation and hardware
    Copyright 2017 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from ...config import ConfigReader
from ...display.hardware import get_hardware_link, Simulator
from ...dbus import DBusClient
from ...core import Arbalet
from ...tools import Rate
from .. import DisplayClient

class DisplayServer(object):
    def __init__(self, parser):
        self.args = parser.parse_args()
        config_reader = ConfigReader()
        self.config = config_reader.hardware
        self.hardware = None
        self.simulation = None
        self.client = None
        host = self.args.server if len(self.args.server) > 0 else '127.0.0.1'
        self.bus = DBusClient(display_subscriber=True, raw_event_publisher=True, background_subscriber=True, host=host)
        self.running = False
        self.arbalet = Arbalet()
        self.start_displays()
        self.rate = Rate(config_reader.hardware['refresh_rate'])

    def start_displays(self):
        factor_sim = 40    # TODO autosize
        if not self.args.no_gui:
            print("[Arbalet Display Server] starting simulation")
            self.simulation = Simulator(self.arbalet, self.arbalet.height*factor_sim, self.arbalet.width*factor_sim)

        if self.args.hardware:
            print("[Arbalet Display Server] starting hardware link")
            self.hardware = get_hardware_link(self.arbalet)

        if len(self.args.server) > 0:
            print("[Arbalet Display Server] Sniffing display from D-Bus server {}".format(self.args.server))

        if len(self.args.proxy) > 0:
            print("[Arbalet Display Server] starting display proxy, forwarding display to {}".format(self.args.proxy))
            self.client = DisplayClient(self.arbalet, self.args.proxy)

    def work(self):
        # Step 1/2: Update the model
        model = self.bus.display.recv(blocking=False)
        background = self.bus.background.recv(blocking=False)

        if model is not None:
            self.arbalet.model.from_dict(model)
        if background is not None:
            self.arbalet.background.from_dict(background)

        # Step 2/2: Read feedback
        events = []
        if self.simulation is not None:
            events += self.simulation.get_touch_events()
        if self.hardware is not None:
            events += self.hardware.get_touch_events()
        for e in events:
            self.bus.raw_events.publish(e)
        self.rate.sleep()


    def run(self):
        self.running = True
        while self.running:
            try:
                self.work()
            except KeyboardInterrupt:
                print("[Arbalet Display server] Shutdown initiated via SIGINT, closing...")
                self.close()
                return

    def close(self):
        self.running = False
        if self.simulation is not None:
            self.simulation.close()
        if self.hardware is not None:
            self.hardware.close()
        if self.client is not None:
            self.client.close()
