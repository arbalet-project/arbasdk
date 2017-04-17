
def get_display_parser(existing_parser):
    """
    Returns the argument parser of a single display server instance
    :param existing_parser: Existing parser from arparse.ArgumentParser (can be an empty parser)
    """
    existing_parser.add_argument('-w', '--hardware',
                                 action='store_true',
                                 help='The server must connect to Arbalet hardware, of kind type described in the configuration file. '
                                      'If false, a simulation will pop up. '
                                      'To display both, two servers must be started. ')

    return existing_parser


def get_user_display_parser(existing_parser):
    """
    Returns the argument parser of the end-user display features
    :param existing_parser: Existing parser from arparse.ArgumentParser (can be an empty parser)
    """
    parser = get_display_parser(existing_parser)

    parser.add_argument('-n', '--no-simulation',
                        dest='simulation',
                        action='store_false',
                        help='Disable the LED/touch device simulation that is automatically started otherwise')

    return parser
