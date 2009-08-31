"""Class for the various animals in the game"""

from pgu.vid import Sprite
from pgu.algo import getline

import imagecache
import tiles
from misc import Position

class Animal(Sprite):
    """Base class for animals"""

    def __init__(self, image_left, image_right, tile_pos):
        # Create the animal somewhere far off screen
        Sprite.__init__(self, image_left, (-1000, -1000))
        self.image_left = image_left
        self.image_right = image_right
        self.pos = Position(tile_pos[0], tile_pos[1])

    def loop(self, tv, _sprite):
        ppos = tv.tile_to_view(self.pos.to_tuple())
        self.rect.x = ppos[0]
        self.rect.y = ppos[1]

    def move(self, state):
        """Given the game state, return a new position for the object"""
        # Default is not to move
        pass

    def _fix_face(self, final_pos):
        """Set the face correctly"""
        if final_pos.left_of(self.pos):
            self.setimage(self.image_left)
        elif final_pos.right_of(self.pos):
            self.setimage(self.image_right)

class Chicken(Animal):
    """A chicken"""

    def __init__(self, pos):
        image_left = imagecache.load_image('sprites/chkn.png')
        image_right = imagecache.load_image('sprites/chkn.png',
                ("right_facing",))
        Animal.__init__(self, image_left, image_right, pos)

    def move(self, gameboard):
        """A free chicken will move away from other free chickens"""
        pass

class Egg(Animal):
    """An egg"""

    def __init__(self, pos):
        image = imagecache.load_image('sprites/egg.png')
        Animal.__init__(self, image, image, pos)

    # Eggs don't move

class Fox(Animal):
    """A fox"""

    costs = {
            # weighting for movement calculation
            'grassland' : 2,
            'woodland' : 1, # Try to keep to the woods if possible
            'broken fence' : 1,
            'fence' : 10,
            'guardtower' : 1, # We can pass under towers
            'henhouse' : 1,
            }

    def __init__(self, pos):
        image_left = imagecache.load_image('sprites/fox.png')
        image_right = imagecache.load_image('sprites/fox.png',
                ("right_facing",))
        Animal.__init__(self, image_left, image_right, pos)
        self.landmarks = [self.pos]
        self.hunting = True
        self.dig_pos = None
        self.tick = 0

    def _cost_path(self, path, gameboard):
        """Calculate the cost of a path"""
        total = 0
        for pos in path:
            if gameboard.in_bounds(pos):
                this_tile = gameboard.tv.get(pos.to_tuple())
                cost = self.costs.get(tiles.TILE_MAP[this_tile], 100)
            else:
                cost = 100 # Out of bounds is expensive
            total += cost
        return total

    def _gen_path(self, start_pos, final_pos):
        """Construct a direct path from start_pos to final_pos,
           excluding start_pos"""
        if abs(start_pos.x - final_pos.x) < 2 and \
                abs(start_pos.y - final_pos.y) < 2:
            # pgu gets this case wrong on occasion.
            return [final_pos]
        start = start_pos.to_tuple()
        end = final_pos.to_tuple()
        points = getline(start, end)
        points.remove(start) # exclude start_pos
        if end not in points:
            # Rounding errors in getline cause this
            points.append(end)
        return [Position(x[0], x[1]) for x in points]

    def _find_best_path_step(self, final_pos, gameboard):
        """Find the cheapest path to final_pos, and return the next step
           along the path."""
        # We calculate the cost of the direct path
        direct_path = self._gen_path(self.pos, final_pos)
        min_cost = self._cost_path(direct_path, gameboard)
        min_path = direct_path
        # is there a point nearby that gives us a cheaper direct path?
        # This is delibrately not finding the optimal path, as I don't
        # want the foxes to be too intelligent, although the implementation
        # isn't well optimised yet
        poss = [Position(x, y) for x in range(self.pos.x - 2, self.pos.x + 3)
                for y in range(self.pos.y - 2, self.pos.y + 3)]
        for start in poss:
            if start == self.pos:
                continue # don't repeat work we don't need to
            cand_path = self._gen_path(self.pos, start) + \
                    self._gen_path(start, final_pos)
            cost = self._cost_path(cand_path, gameboard)
            if cost < min_cost:
                min_cost = cost
                min_path = cand_path
        if not min_path:
            return final_pos
        return min_path[0]

    def _find_path_to_woodland(self, gameboard):
        """Dive back to woodland through the landmarks"""
        # find the closest point to our current location in walked path
        if self.pos == self.landmarks[-1]:
            if len(self.landmarks) > 1:
                self.landmarks.pop() # Moving to the next landmark
            else:
                # Safely back at the start
                return self.pos
        return self._find_best_path_step(self.landmarks[-1], gameboard)

    def _find_path_to_chicken(self, gameboard):
        """Find the path to the closest chicken"""
        # Find the closest chicken
        min_dist = 999
        closest = None
        for chicken in gameboard.chickens:
            dist = chicken.pos.dist(self.pos)
            if dist < min_dist:
                min_dist = dist
                closest = chicken
        if not closest:
            # No more chickens, so leave
            self.hunting = False
            return self.pos
        if closest.pos == self.pos:
            # Caught a chicken
            gameboard.remove_chicken(closest)
            self.hunting = False
            return self.pos
        return self._find_best_path_step(closest.pos, gameboard)

    def _update_pos(self, gameboard, new_pos):
        """Update the position, making sure we don't step on other foxes"""
        final_pos = new_pos
        moves = [Position(x, y) for x in range(self.pos.x-1, self.pos.x + 2)
                for y in range(self.pos.y-1, self.pos.y + 2)]
        blocked = False
        for fox in gameboard.foxes:
            if fox is not self and fox.pos == new_pos:
                blocked = True
            if fox.pos in moves:
                moves.remove(fox.pos)
        if blocked:
            # find the closest point in moves to new_pos that's not a fence
            final_pos = None
            dist = 10
            for poss in moves:
                this_tile = gameboard.tv.get(poss.to_tuple())
                new_dist = poss.dist(new_pos)
                if new_dist < dist:
                    dist = new_dist
                    final_pos = poss
        this_tile = gameboard.tv.get(final_pos.to_tuple())
        if tiles.TILE_MAP[this_tile] == 'broken fence' and self.hunting:
            # We'll head back towards the holes we make/find
            self.landmarks.append(final_pos)
        elif tiles.TILE_MAP[this_tile] == 'fence' and not self.dig_pos:
            self.tick = 5
            self.dig_pos = final_pos
            return self.pos
        return final_pos

    def move(self, gameboard):
        """Foxes will aim to move towards the closest henhouse or free
           chicken"""
        if self.dig_pos:
            if self.tick:
                # We're digging through the fence
                self.tick -= 1
                # Check the another fox hasn't dug a hole for us
                # We're top busy digging to notice if a hole appears nearby,
                # but we'll notice if the fence we're digging vanishes
                this_tile = gameboard.tv.get(self.dig_pos.to_tuple())
                if tiles.TILE_MAP[this_tile] == 'broken fence':
                    self.tick = 0 
            else:
                # We've dug through the fence, so make a hole
                gameboard.tv.set(self.dig_pos.to_tuple(),
                        tiles.REVERSE_TILE_MAP['broken fence'])
                self.dig_pos = None
            return 
        if self.hunting:
            desired_pos = self._find_path_to_chicken(gameboard)
        else:
            desired_pos = self._find_path_to_woodland(gameboard)
        final_pos = self._update_pos(gameboard, desired_pos)
        self._fix_face(final_pos)
        self.pos = final_pos
        
            
