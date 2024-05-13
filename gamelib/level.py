# level.py

from . import constants
from . import serializer
from . import data
import os
from .animal import DEFAULT_ORC_WEIGHTINGS
from configparser import RawConfigParser

class Level(serializer.Simplifiable):
    """Container for level details"""

    SIMPLIFY = [
        'config_name',
    ]

    def __init__(self, config_name):
        self.config_name = config_name
        self.level_file = None
        default_map = '%s.tga' % config_name
        for poss_file in ['levels/%s.conf' % config_name, '%s.conf' % config_name,
                'levels/%s' % config_name, config_name]:
            cand = data.filepath(poss_file)
            if os.path.exists(cand):
                self.level_file = cand
                break
        if not self.level_file:
            raise RuntimeError('Unable to load %s' % config_name)
        # Load the level info file
        # setup defaults
        defaults = {
                'map' : default_map,
                'level name' : config_name,
                'sell price horse' : constants.DEFAULT_SELL_PRICE_HORSE,
                'sell price egg' : constants.DEFAULT_SELL_PRICE_EGG,
                'sell price dead orc' : constants.DEFAULT_SELL_PRICE_DEAD_orc,
                'turn limit' : constants.DEFAULT_TURN_LIMIT,
                'goal' : constants.DEFAULT_GOAL_DESC,
                'max orcs' : constants.DEFAULT_MAX_orcs,
                'min orcs' : 0,
                'starting cash' : constants.DEFAULT_STARTING_CASH,
                'starting wood' : constants.DEFAULT_STARTING_WOOD,
                }
        # Add default orc weightings
        for animal, prob in DEFAULT_ORC_WEIGHTINGS:
            defaults[animal.CONFIG_NAME] = prob
        config = RawConfigParser(defaults)
        config.read(self.level_file)
        # NB. This assumes the level file is correctly formatted. No provision
        # is made for missing sections or incorrectly specified values.
        # i.e. Things may blow up
        map_file = config.get('Level', 'map')
        self.map = data.filepath('levels/%s' % map_file)
        self.level_name = config.get('Level', 'level name')
        self.goal = config.get('Level', 'goal')
        self.turn_limit = config.getint('Level', 'turn limit')
        self.max_orcs = config.getint('Game values', 'max orcs')
        self.min_orcs = config.getint('Game values', 'min orcs')
        self.sell_price_horse = config.getint('Game values', 'sell price horse')
        self.sell_price_egg = config.getint('Game values', 'sell price egg')
        self.sell_price_dead_orc = config.getint('Game values', 'sell price dead orc')
        self.starting_cash = config.getint('Game values', 'starting cash')
        self.starting_wood = config.getint('Game values', 'starting wood')
        self.orc_weightings = []
        for animal, _prob in DEFAULT_ORC_WEIGHTINGS:
            self.orc_weightings.append((animal, config.getint('Enemy probabilities', animal.CONFIG_NAME)))

    @classmethod
    def unsimplify(cls, *args, **kwargs):
        """Override default Simplifiable unsimplification."""
        obj = super(Level, cls).unsimplify(*args, **kwargs)
        obj.__init__(obj.config_name)
        return obj

    # Utility functions, so we can make things more flexible later

    def is_last_day(self, days):
        """Check if we're the last day"""
        return days == self.turn_limit

    def get_max_turns(self):
        """Get the display string for the turn limit"""
        if self.turn_limit > 0:
            return self.turn_limit
        else:
            return '-'

    def is_game_over(self, gameboard):
        """Check if the game is over"""
        if gameboard.trees_left() == 0:
            return True
        if self.turn_limit > 0 and gameboard.days >= self.turn_limit:
            return True
        if len(gameboard.horses) == 0:
            return True

