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
from os.path import isfile, isdir, join, realpath, dirname, expanduser
from shutil import copyfile
from os import chdir, makedirs, access, W_OK
from sys import executable
from json import load
from subprocess import Popen
from glob import glob
from time import sleep, time
from signal import SIGINT, signal
from copy import deepcopy


class Sequencer(object):
    def __init__(self, parser):
        self.args =  parser.parse_args()
        self.running = False
        signal(SIGINT, self.close_processes)
        self.config = ConfigReader()
        self.command = None
        self.current_app_index = 0
        self.events = EventClient('127.0.0.1')
        self.white_list = self.get_authorized_apps()

    def close_processes(self, signal, frame):
        self.running = False

    def get_authorized_apps(self):
        white_list_file = join(realpath(dirname(__file__)), 'sequences', 'white_list.json')  # Owned by root
        if isfile(white_list_file):
            # Security check: the user must not have write access to the white list
            if access(white_list_file, W_OK):
                print("[Arbalet Sequencer] Current user has write access to {} but shouldn't for security reasons, denied access to apps".format(white_list_file))
                return []
            with open(white_list_file) as f:
                return load(f)
        return []

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

    def wait(self, timeout=-1, interruptible=True, process=None):
        start = time()
        # We loop while the process is not terminated, the timeout is not expired, and user has not asked 'next' with the joystick
        while self.running and (timeout < 0 or time()-start < timeout) and (process is None or process.poll() is None):
            if self.command is not None:
                return 'new_launch'
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
        return 'timeout' if (process is None or process.poll() is None) else 'terminated'

    def execute_sequence(self, sequence):
        def purify_args(args):
            for rm_arg in ['-h, --hardware', '-ng', '-no-gui', '-s', '--server']:
                try:
                    args.remove(rm_arg)
                except ValueError:
                    pass
            return args

        def expand_args(args, cwd):          
            #args = map(lambda arg: if len(glob(join(cwd, arg))) > 0 else arg, args)  # Expand . ? and *
            expanded_args = []
            for arg in args:
                globed_arg = glob(arg)
                if len(globed_arg)==0:
                    expanded_args.append(arg)
                else:
                    for expanded_arg in globed_arg:
                        expanded_args.append(expanded_arg)
            return expanded_args

        # change WD to the modules' root
        #cwd = join(realpath(dirname(__file__)), '..', '..', 'apps')
        #chdir(cwd)

        rate = Rate(1)
        self.running = True

        while self.running:
            command = deepcopy(self.command)
            self.command = None

            if command is None:
                command = sequence['sequence'][self.current_app_index]
                self.current_app_index = (self.current_app_index + 1) % len(sequence['sequence'])

            if command['app'] not in self.white_list:
                print("[Arbalet Sequencer] Skipping {} not allowed in application white list".format(command['app']))
            else:
                args = "{} -m arbalet.apps.{} {}".format(executable, command['app'], command['args'] if 'args' in command else '')
                module_command = purify_args(expand_args(args.split(), join(*command['app'].split('.'))))
                while self.running:  # Loop allowing the user to play again, by restarting app
                    print("[Arbalet Sequencer] STARTING {}".format(module_command))
                    process = Popen(module_command)#, cwd=cwd)
                    timeout = command['timeout'] if 'timeout' in command else -1
                    reason = self.wait(timeout, True, process) # TODO interruptible raw_input in new_thread for 2.7, exec with timeout= for 3
                    print("[Arbalet Sequencer] END: {}".format(reason))
                    if reason != 'terminated' or not self.running:
                        process.send_signal(SIGINT)
                        process.wait()
                    if reason != 'restart':
                        break
            rate.sleep()
