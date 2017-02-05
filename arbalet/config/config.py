from os import path
from json import load
from configparser import RawConfigParser


def get_config_parser(existing_parser):
    existing_parser.add_argument('-c', '--config',
                                 type=str,
                                 default='',
                                 help='Name of the config file describing the hardware (.json file). '
                                      'If missing the default config in arbasdk/arbalet/default.cfg will be selected')
    return existing_parser


class ConfigReader(object):
    """
    Arbalet configuration file reader
    Open and loads the default configuration file or the specified configuration
    """
    def __init__(self, config='', joystick_config=''):
        # First fetch the right configuration files and check their presence
        if config == '' or joystick_config == '':
            cfg_path = path.join(path.dirname(__file__), '..', 'config', 'default.cfg')
            cfg_parser = RawConfigParser()
            cfg_parser.read(cfg_path)
            if config == '':
                config = cfg_parser.get('DEFAULT', 'config')
            if joystick_config == '':
                joystick_config = cfg_parser.get('DEFAULT', 'joystick')

        if not path.isfile(config):
            config = path.join(path.dirname(__file__), '..', 'config', config)
        if not path.isfile(config):
            raise IOError("Config file '{}' not found".format(config))

        if not path.isfile(joystick_config):
            joystick_config = path.join(path.dirname(__file__), '..', 'config', joystick_config)
        if not path.isfile(joystick_config):
            raise IOError("Joystick mapping file '{}' not found".format(joystick_config))

        dbus_config = path.join(path.dirname(__file__), '..', 'config', 'dbus.json')
        if not path.isfile(dbus_config):
            raise IOError("D-Bus config file 'dbus.json' not found".format())

        font_config = path.join(path.dirname(__file__), '..', 'config', 'font.json')
        if not path.isfile(dbus_config):
            raise IOError("Font config file 'font.json' not found".format())

        # Now load all configuration files
        try:
            with open(config, 'r') as f:
                self._config = load(f)
        except ValueError as e:
            raise ValueError(
                "Configuration file {} has an incorrect format, make sure it is a valid JSON. {}".format(config, str(e)))
        except IOError as e:
            raise IOError("Configuration file {} can't be read. {}".format(config, str(e)))
        else:
            # Add additional handy attributes
            self._config['height'] = len(self._config['mapping'])
            self._config['width'] = len(self._config['mapping'][0]) if self._config['height'] > 0 else 0

        try:
            with open(joystick_config, 'r') as f:
                self._joystick = load(f)
        except ValueError as e:
            raise ValueError(
                "Joystick mapping file {} has an incorrect format, make sure it is a valid JSON. {}".format(joystick_config,
                                                                                                            str(e)))
        except IOError as e:
            raise IOError("Joystick mapping file {} can't be read. {}".format(joystick_config, str(e)))

        try:
            with open(dbus_config, 'r') as f:
                self._dbus = load(f)
        except ValueError as e:
            raise ValueError(
                "D-Bus configuration file {} has an incorrect format, make sure it is a valid JSON. {}".format(dbus_config,
                                                                                                               str(e)))
        except IOError as e:
            raise IOError("D-Bus configuration file {} can't be read. {}".format(dbus_config, str(e)))

        try:
            with open(font_config, 'r') as f:
                self._font = load(f)
        except ValueError as e:
            raise ValueError(
                "Font configuration file {} has an incorrect format, make sure it is a valid JSON. {}".format(font_config,
                                                                                                               str(e)))
        except IOError as e:
            raise IOError("Font configuration file {} can't be read. {}".format(font_config, str(e)))

    @property
    def hardware(self):
        return self._config

    @property
    def joystick(self):
        return self._joystick

    @property
    def dbus(self):
        return self._dbus

    @property
    def font(self):
        return self._font