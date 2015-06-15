#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='arbalet',
    version='0.0.1',
    license="GNU General Public License 3",
    description="Python API and examples for development with Arbalet LED tables (ARduino-BAsed LEd Table)",
    url='http://github.com/arbalet-project',
    author="Yoan Mollard",
    author_email="contact@konqi.fr",
    long_description=open('README.md').read(),

    install_requires= ["pygame", "pyserial", "bottle", "python-midi", "pyaudio", "zmq", "python-xlib", "PIL"],
    include_package_data=True,
    zip_safe=False,  # contains data files

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Games/Entertainment",
    ],

    data_files=[('hardware/arduino/arbalink', ['hardware/arduino/arbalink/arbalink.ino']),  # TODO place in Arduino IDE's default workspace?
                ('config', ['config/config150.json']),
                ('config', ['config/default.cfg'])
    ],

    packages=find_packages(),
)
