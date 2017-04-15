from multiprocessing import Process, Event
from os import kill
from signal import SIGINT
from ..dbus.proxy import Proxy
from ..events.server import EventServer
from ..config import ConfigReader
from ..display.server import DisplayServer


class Servers(object):
    """
    Background servers to run the app in standalone mode
    Must only be used in one-shot runs, as in normal use services are already running in background
    """
    def __init__(self, hardware, simulation):
        self.processes = []
        self.hardware = hardware
        self.simulation = simulation
        config_reader = ConfigReader()
        self.config = config_reader.hardware
        self.processes = []
        self.stop_event = Event()

    def start(self):
        self.processes.append(Process(target=lambda: Proxy().run()))
        self.processes.append(Process(target=lambda: EventServer('127.0.0.1').run()))

        if self.hardware:
            self.processes.append(Process(target=lambda: DisplayServer(hardware=True).run()))

        if self.simulation:
            self.processes.append(Process(target=lambda:DisplayServer(hardware=False).run()))

        for process in self.processes:
            process.start()

    def stop(self, is_keyboard_interrupt):
        if not is_keyboard_interrupt:
            # Do not send a new signal, a SIGINT sent to a parent is always propagated to children
            for process in self.processes:
                kill(process.pid, SIGINT)

        print("[Standalone run] Waiting for servers to shutdown")
        for process in self.processes:
            process.join()
        print("[Standalone run] All servers off, exiting.")