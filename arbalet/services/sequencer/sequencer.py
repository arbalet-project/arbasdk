#!/usr/bin/env python
"""
    Arbalet - ARduino-BAsed LEd Table
    Sequencer of Arbalet applications

    Runs and closes Arbalet apps according to a sequence file

    Copyright 2017 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from ...events import EventClient
from ...tools import Rate
from ...config import ConfigReader
from ...application import Application
from .apps import AppManager
from os.path import isfile, isdir, join, realpath, dirname, expanduser
from shutil import copyfile
from os import makedirs
from json import load
from time import sleep, time


class Sequencer(Application):
    def __init__(self, **kwargs):
        super(Sequencer, self).__init__(fake=True, **kwargs)
        self.running = False
        self.config = ConfigReader()
        self.current_app_index = 0
        self.events = EventClient('127.0.0.1')
        self.apps = AppManager()

    def get_sequence_file(self):
        home = expanduser("~")
        app_dir = join(home, ".arbalet")  # TODO make cross-plateform
        sequence_file = join(app_dir, "sequence.json")                                          # Owned by user
        default_sequence_file = join(realpath(dirname(__file__)), 'sequences', 'default.json')  # Owned by root

        if not isdir(app_dir):
            try:
                makedirs(app_dir)
            except IOError as e:
                pass

        if not isfile(sequence_file):
            if isfile(default_sequence_file):
                try:
                    copyfile(default_sequence_file, sequence_file)
                except IOError as e:
                    return None
                else:
                    print("[Arbalet Sequencer] Creating sequence file for this user")
            else:
                return None

        if isfile(sequence_file):
            return sequence_file
        elif isfile(default_sequence_file):
            return default_sequence_file
        else:
            return None

    def run(self):
        sequence_file = self.get_sequence_file()
        if sequence_file is None or not isfile(sequence_file):
            print("[Arbalet Sequencer] Can't open sequence file {}".format(sequence_file))
        else:
            # read the sequence
            with open(sequence_file) as fsequence:
                sequence = load(fsequence)
            # and launch every app in the sequence as a client
            self.execute_sequence(sequence)

    def wait(self, name, timeout=-1, interruptible=True):
        start = time()
        # We loop while the process is not terminated, the timeout is not expired, and user has not asked 'next' with the joystick
        while self.running and (timeout < 0 or time()-start < timeout) and self.apps.is_running(name):
            #print("TODO1 new launch")
            #if self.command is not None:
            #    return 'new_launch'
            for e in self.events.get():
                try:
                    select = e['device']['type'] == 'joystick' and e['pressed'] and e['key'] in self.config.joystick['back']
                    start = e['device']['type'] == 'joystick' and e['pressed'] and e['key'] in self.config.joystick['start']
                except KeyError:
                    pass
                else:
                    if interruptible and select:
                        # A "back" joystick key jumps to the next app, unless interruptible has been disabled
                        return 'joystick'
                    elif interruptible and start:
                        # A "start" joystick key restarts the same app
                        return 'restart'
                    else:
                        # Any other activity resets the timer
                        start = time()
            sleep(0.01)
        return 'timeout' if self.apps.is_running(name) else 'terminated'

    def execute_sequence(self, sequence):
        # change WD to the modules' root
        #cwd = join(realpath(dirname(__file__)), '..', '..', 'apps')
        #chdir(cwd)

        rate = Rate(1)
        self.running = True
        while self.running:
            command = None
            if command is None:
                command = sequence['sequence'][self.current_app_index]
                print(command)
                name = command['name']
                args = command['args'] if 'args' in command else {}
                while self.running:  # Loop allowing the user to play again, by restarting app
                    print("[Arbalet Sequencer] STARTING {}".format(name, args))
                    self.apps.run(command['name'], args)

                    # Load next app
                    #next_command = sequence['sequence'][(self.current_app_index + 1) % len(sequence['sequence'])]
                    #next_name = next_command['name']
                    #next_args = next_command['args'] if 'args' in next_command else {}
                    #self.apps.load(next_name, next_args)

                    # Monitor current app
                    timeout = command['timeout'] if 'timeout' in command else -1
                    reason = self.wait(name, timeout, True)

                    print("[Arbalet Sequencer] END: {}".format(reason))
                    self.apps.stop(name)
                    if reason != 'restart':
                        break
            self.current_app_index = (self.current_app_index + 1) % len(sequence['sequence'])
            rate.sleep()
