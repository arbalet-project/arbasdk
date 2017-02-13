import argparse
from .server import EventServer
from ...config import get_config_parser

parser = argparse.ArgumentParser(description='Arbalet Event Manager. '
                                             'Gathers all events from sensors, i.e. keyboards, joysticks, touch sensors, '
                                             'web interfaces and publishes them on the Arbalet D-BUS.'
                                             'Interactive applications will not properly work without running Event Manager.')

parser.add_argument('-s', '--server',
                    type=str,
                    nargs='?',
                    const=True,
                    default='localhost',
                    help='IP or hostname of the D-Bus server to send events to (ex: myserver.local, 192.168.0.15, ...)'
                         'Do not provide port, it is specified in the D-Bus configuration file')

parser.add_argument('-v', '--verbose',
                    action='store_const',
                    const=True,
                    default=False,
                    help='Print individual events produced by controls mapping ans streamed to user apps')

parser = get_config_parser(parser)
EventServer(parser).run()