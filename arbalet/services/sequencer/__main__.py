import argparse
from .sequencer import Sequencer
from ...application import get_application_parser

parser = argparse.ArgumentParser(description='Arbalet application sequencer. Runs and closes Arbalet apps according to a sequence file. '
                                             'The sequence file is ~/.arbalet/sequencer.json, it is created with a default sequence if unexisting, or a default sequence is used. '
                                             'The sequence can then be modified by the user in its homedir. ')

parser = get_application_parser(parser)
args = parser.parse_args()
Sequencer(**args.__dict__).start()
