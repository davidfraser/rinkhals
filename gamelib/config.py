# level.py

from ConfigParser import RawConfigParser
from optparse import OptionParser

class Config(object):
    """Container for various global configuration knobs and levers."""

    valid_options = {
        'sound': {'type': 'boolean', 'default': 'true'},
        'level_name': {'type': 'string', 'default': 'two_weeks'},
        }

    config_filename = 'config.ini'

    def configure(self, params=None):
        self._config = RawConfigParser(dict(
                [(k, v['default']) for k, v in self.valid_options.items() if 'default' in v]
            ))
        self._config.add_section('Options')
        self._set_up_params(params)
        self._config.read(self.config_filename)
        self._process_params()

    def _set_up_params(self, params):
        parser = OptionParser()
        parser.add_option("-c", "--config", metavar="FILE", dest="config_filename",
                          help="read configuration from FILE")
        parser.add_option("-l", "--level", metavar="LEVEL", dest="level_name",
                          help="select level LEVEL")
        parser.add_option("--sound", action="store_const", const="on", dest="sound",
                          help="enable sound")
        parser.add_option("--no-sound", action="store_const", const="off", dest="sound",
                          help="disable sound")
        (self._opts, _) = parser.parse_args(params or [])
        self.config_filename = self._opts.config_filename or self.config_filename

    def _process_params(self):
        for name in self.valid_options:
            opt = getattr(self._opts, name)
            if opt is not None:
                self._config.set('Options', name, opt)

    def __getattr__(self, name):
        if name not in self.valid_options:
            raise AttributeError(name)
        get_methods = {
            'string': lambda n: self._config.get('Options', n),
            'boolean': lambda n: self._config.getboolean('Options', n),
            }
        return get_methods[self.valid_options[name].get('type', 'string')](name)

# Here's a global variable. Don't try this at home, kids!
config = Config()