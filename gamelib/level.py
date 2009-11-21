# level.py

import constants
import data
import os
from animal import DEFAULT_FOX_WEIGHTINGS
from ConfigParser import RawConfigParser

class Level(object):
    """Container for level details"""

    def __init__(self, level_name):
        self.level_file = None
        default_map = '%s.tga' % level_name
        for poss_file in ['levels/%s.conf' % level_name, '%s.conf' % level_name,
                'levels/%s' % level_name, level_name]:
            cand = data.filepath(poss_file)
            if os.path.exists(cand):
                self.level_file = cand
                break
        if not self.level_file:
            raise RuntimeError('Unable to load %s' % level_name)
        # Load the level info file
        # setup defaults
        defaults = {
                'map' : default_map,
                'level name' : level_name,
                'sell price chicken' : constants.DEFAULT_SELL_PRICE_CHICKEN,
                'sell price egg' : constants.DEFAULT_SELL_PRICE_EGG,
                'sell price dead fox' : constants.DEFAULT_SELL_PRICE_DEAD_FOX,
                'turn limit' : constants.DEFAULT_TURN_LIMIT,
                'goal' : constants.DEFAULT_GOAL_DESC,
                'max foxes' : constants.DEFAULT_MAX_FOXES,
                'min foxes' : 0,
                'starting cash' : constants.DEFAULT_STARTING_CASH,
                }
        # Add default fox weightings
        for animal, prob in DEFAULT_FOX_WEIGHTINGS:
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
        self.max_foxes = config.getint('Game values', 'max foxes')
        self.min_foxes = config.getint('Game values', 'min foxes')
        self.sell_price_chicken = config.getint('Game values', 'sell price chicken')
        self.sell_price_egg = config.getint('Game values', 'sell price egg')
        self.sell_price_dead_fox = config.getint('Game values',
                'sell price dead fox')
        self.starting_cash = config.getint('Game values', 'starting cash')
        self.fox_weightings = []
        for animal, _prob in DEFAULT_FOX_WEIGHTINGS:
            self.fox_weightings.append((animal, config.getint('Fox probablities',
                animal.CONFIG_NAME)))

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
        if len(gameboard.chickens) == 0:
            return True

