import argparse
from .server import DisplayServer
from .parser import get_display_parser
from ...config import get_config_parser

parser = argparse.ArgumentParser(description='Arbalet Display Server. '
                                             'Gathers all models and layers from D-Bus, and dispatches them on simulation and hardware. '
                                             'Applications will work but not show without running Display Server. '
                                             'Several servers can be run')

parser.add_argument('-s', '--source',
                    type=str,
                    nargs='?',
                    const=True,
                    default='',
                    help='IP or hostname of the D-Bus server to sniff the display from. '
                         'E.g. myserver.local, 192.168.0.15, ...  '
                         'If not argument is provided D-Bus is assumed to be localhost (default). '
                         'Do not provide port, it is specified in the D-Bus configuration file')

parser = get_display_parser(parser)
parser = get_config_parser(parser)
args = parser.parse_args()

DisplayServer(args.hardware).run()