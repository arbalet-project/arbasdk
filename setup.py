#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os import listdir
from os.path import join

config_dir = join('arbalet', 'config')
json_config_files = (config_dir, [join(config_dir, file) for file in listdir(config_dir) if '.json' in file])

setup(
    name='arbalet_core',
    version='2.0.0',
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
    namespace_packages = ['arbalet']
)
