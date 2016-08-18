#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='arbalet_core',
    version='1.0.0',
    license="GNU General Public License 3",
    description="Python API for development with Arbalet LED tables (ARduino-BAsed LEd Table)",
    url='http://github.com/arbalet-project',
    author="Yoan Mollard",
    author_email="contact@konqi.fr",
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

    data_files=[('arbalet/config', ['arbalet/config/config150.json']),
                ('arbalet/config', ['arbalet/config/config150touch.json']),
                ('arbalet/config', ['arbalet/config/default.cfg']),
                ('arbalet/config', ['arbalet/config/joyF710.json']),
                ('arbalet/config', ['arbalet/config/joyRumblepad.json']),
                ('arbalet/core', ['arbalet/core/icon.png'])
    ],

    packages=find_packages(),
    namespace_packages = ['arbalet']
)
