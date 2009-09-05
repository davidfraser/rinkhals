# Holder for misc useful classes

import random

class Position(object):
    """2D position / vector"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_tuple(self):
        return self.x, self.y

    def dist(self, b):
        """Gives the distance to another position"""

        return max(abs(self.x - b.x), abs(self.y - b.y))

    def __sub__(self, b):
        return Position(self.x - b.x, self.y - b.y)

    def __add__(self, b):
        return Position(self.x + b.x, self.y + b.y)

    def left_of(self, b):
        return self.x < b.x

    def right_of(self, b):
        return self.x > b.x

    def __eq__(self, b):
        return self.x == b.x and self.y == b.y

class WeightedSelection(object):
    def __init__(self, weightings=None):
        self.weightings = []
        self.total = 0
        if weightings:
            for item, weight in weightings:
                self.weightings.append((item, weight))
                self.total += weight
        
    def choose(self):
        roll = random.uniform(0, self.total)
        for item, weight in self.weightings:
            if roll < weight:
                return item
            roll -= weight
