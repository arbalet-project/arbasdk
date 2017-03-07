from subprocess import Popen
from sys import executable
from signal import SIGINT


class Servers(object):
    """
    Background servers to run the app in standalone mode
    Must only be used in one-shot runs, as in normal use services are already running in background
    """
    def __init__(self, hardware, no_gui):
        self.processes = []
        self.hardware = hardware
        self.no_gui = no_gui

    def start(self):
        self.processes.append(Popen("{} -m arbalet.dbus.proxy".format(executable).strip().split()))
        self.processes.append(Popen("{} -m arbalet.events.server".format(executable).strip().split()))
        hardware = "--hardware" if self.hardware else ""
        no_gui = "--no-gui" if self.no_gui else ""
        display_params = " ".join(filter(None, [hardware, no_gui]))
        self.processes.append(Popen("{} -m arbalet.display.server {}".format(executable, display_params).strip().split(' ')))

    def stop(self):
        for process in self.processes:
            process.send_signal(SIGINT)
        print("[Standalone run] Waiting for servers to shutdown")
        for process in self.processes:
            process.wait()   # TODO use timeout=