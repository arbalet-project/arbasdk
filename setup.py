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

    install_requires= ["pygame", "pyserial", "bottle", "python-midi", "pyalsaaudio", "zmq", "python-xlib", "Pillow", "numpy"],
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

    data_files=[('config', ['config/config150.json']),
                ('config', ['config/config150touch.json']),
                ('config', ['config/default.cfg']),
                ('config', ['config/joyF710.json']),
                ('config', ['config/joyRumblepad.json']),
                ('arbasdk', ['arbasdk/icon.png'])
    ],

    packages=find_packages(),
)
