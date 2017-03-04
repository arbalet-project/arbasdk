import argparse
from .server import DisplayServer
from .parser import get_display_parser
from ...config import get_config_parser

parser = argparse.ArgumentParser(description='Arbalet Display Server. '
                                             'Gathers all models and layers from D-Bus, and dispatches them on simulation and hardware. '
                                             'Applications will work but not show without running Display Server.')

parser.add_argument('-s', '--server',
                    type=str,
                    nargs='?',
                    const=True,
                    default='',
                    help='IP or hostname of the D-Bus server to sniff the display from. '
                         'E.g. myserver.local, 192.168.0.15, ...  '
                         'If not argument is provided D-Bus is assumed to be localhost (default). '
                         'Do not provide port, it is specified in the D-Bus configuration file')

parser.add_argument('-x', '--proxy',
                    type=str,
                    nargs='?',
                    const=True,
                    default='',
                    help='IP or hostname of the display servers to forward the display to. '
                         'E.g. myserver.local, 192.168.0.15, ... '
                         'Only used if this server is a proxy (aka broker) and output stream has to be forwarded to another server '
                         'If not argument is provided this server will be an end point (default). '
                         'Do not provide port, it is specified in the D-Bus configuration file')

parser = get_display_parser(parser)
parser = get_config_parser(parser)
DisplayServer(parser).run()