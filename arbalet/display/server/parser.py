def get_display_parser(existing_parser):
    existing_parser.add_argument('-w', '--hardware',
                                 action='store_true',
                                 help='The server must connect to Arbalet hardware, of kind type described in the configuration file. '
                                      'If false, a simulation will pop up. '
                                      'To display both, two servers must be started. ')

    return existing_parser