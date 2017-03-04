def get_display_parser(existing_parser):
    existing_parser.add_argument('-w', '--hardware',
                                 action='store_true',

                                 help='The server must connect to Arbalet hardware, of kind type described in the configuration file')

    existing_parser.add_argument('-ng', '--no-gui',
                                 action='store_true',
                                 help='Disable the simulation 2D window started by default on the workstation')
    return existing_parser