from multiprocessing import Process
from ..dbus.proxy import Proxy
from ..events.server import EventServer
from ..display.server import DisplayServer


class Servers(object):
    """
    Background servers to run the app in standalone mode
    Must only be used in one-shot runs, as in normal use services are already running in background
    """
    def __init__(self, argparser):
        self.processes = []
        self.argparser = argparser

    def start(self):
        self.processes.append(Process(target=lambda: Proxy(self.argparser).run()))
        self.processes.append(Process(target=lambda: EventServer(self.argparser).run()))
        self.processes.append(Process(target=lambda: DisplayServer(self.argparser).run()))

        for process in self.processes:
            process.start()

    def stop(self):
        for process in self.processes:
            process.terminate()  # Would be SIGINT nicer?

        print("[Standalone run] Waiting for servers to shutdown")
        for process in self.processes:
            process.join()
        print("[Standalone run] All servers off, exiting.")