# Holder for misc useful classes

class Position(object):
   """2D position / vector"""

   def __init__(self, x, y):
       self.x = x
       self.y = y

   def to_tuple(self):
       return self.x, self.y

   def dist(self, b):
       """Gives the distance to another position"""

       return abs(self.x - b.x) + abs(self.y - b.y)

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
