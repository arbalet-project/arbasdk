#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join, isdir, expanduser, exists, realpath
from os import listdir

config_dir = join('arbalet', 'config')
json_config_files = (config_dir, [join(config_dir, file) for file in listdir(config_dir) if '.json' in file])

setup(
    name='arbalet_sdk',
    version='4.0.0',
    license="GNU General Public License 3",
    description="Python API for development with Arbalet LED tables (ARduino-BAsed LEd Table)",
    url='http://github.com/arbalet-project',
    author="Yoan Mollard",
    author_email="contact@arbalet-project.org",
    long_description=open('README.md').read(),

    install_requires= ["pygame", "configparser", "pyserial", "zmq", "numpy"],
    include_package_data=True,
    zip_safe=False,  # contains data files

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment",
    ],

    data_files=[('arbalet/config', ['arbalet/config/default.cfg']),
                ('arbalet/core', ['arbalet/core/icon.png']),
                json_config_files
    ],

    packages=find_packages(),
    namespace_packages = ['arbalet', 'arbalet.events', 'arbalet.dbus']
)

## Install Arduino librairies on Unix OSes
try:
    from os import symlink
except ImportError:
    print('Skipping Arduino libs simlinking on non-Unix system')
else:
    lib_path = join('hardware', 'arduino')
    lib_files = [(file.replace('-', '_'), join(lib_path, file)) for file in listdir(lib_path)]
    libs = [(file, realpath(full_file)) for file, full_file in lib_files if isdir(full_file)]

    arduino_lib_dir = join(expanduser("~"), 'sketchbook', 'libraries')

    if isdir(arduino_lib_dir):
        for lib_name, lib_path in libs:
            target_lib = join(arduino_lib_dir, lib_name)
            if not exists(target_lib):
                print('Simlinking arduino lib {} in {}'.format(lib_name, arduino_lib_dir))
                symlink(lib_path, target_lib)
            else:
                print('Skipping arduino lib {} simlinking in {}: target already exists'.format(lib_name, arduino_lib_dir))
