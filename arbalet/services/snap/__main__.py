from .snap import SnapServer
from arbalet.application import get_application_parser
from argparse import ArgumentParser

parser = ArgumentParser(description='Server for the Snap visual programming language. '
                                    'First start the server as any other Arbalet application and keep it open, it runs in background. '
                                    'Open the online Snap environment in your web browser: http://snap.berkeley.edu/run '
                                    'then select File > Import and choose the file "xml/arbalet.xml" file on your local disk')

parser = get_application_parser(parser)
args = parser.parse_args()

SnapServer(33450, **args.__dict__).start()
