"""
    Arbalet - ARduino-BAsed LEd Table

    Arbalet Display Server
    Gathers all models and layers from D-Bus, and dispatches them on simulation and hardware
    Copyright 2017 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from ...config import ConfigReader
from ...display.hardware import get_hardware_link
from ...display import Simulator, DisplayClient
from ...dbus import DBusClient
from ...core import Arbalet


class DisplayServer(object):
    def __init__(self, parser):
        self.args = parser.parse_args()
        config_reader = ConfigReader()
        self.config = config_reader.hardware
        self.hardware = None
        self.simulation = None
        self.client = None
        self.bus = DBusClient(display_subscriber=True)
        self.running = False
        self.arbalet = Arbalet()
        self.start_displays()

    def start_displays(self):
        factor_sim = 40    # TODO autosize
        if not self.args.no_gui:
            print("[Arbalet Display Server] starting simulation")
            self.simulation = Simulator(self.arbalet, self.arbalet.height*factor_sim, self.arbalet.width*factor_sim)

        if self.args.hardware:
            print("[Arbalet Display Server] starting hardware link")
            self.hardware = get_hardware_link(self.arbalet)

        if len(self.args.server) > 0:
            print("[Arbalet Display Server] starting stream forwarding to {}".format(self.args.server))
            self.client = DisplayClient(self.args.server)

    def work(self):
        model = self.bus.display.recv(blocking=True)
        self.arbalet.model.from_dict(model)

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