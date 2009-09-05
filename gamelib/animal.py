"""Class for the various animals in the game"""

import random

from pgu.vid import Sprite
from pgu.algo import getline

import imagecache
import tiles
from misc import Position
import sound
import equipment
import animations

class Animal(Sprite):
    """Base class for animals"""

    STEALTH = 0
    VISION_BONUS = 0
    VISION_RANGE_PENALTY = 10

    def __init__(self, image_left, image_right, tile_pos):
        # Create the animal somewhere far off screen
        Sprite.__init__(self, image_left, (-1000, -1000))
        self._image_left = image_left
        self.image_left = image_left.copy()
        self._image_right = image_right
        self.image_right = image_right.copy()
        if hasattr(tile_pos, 'to_tuple'):
            self.pos = tile_pos
        else:
            self.pos = Position(tile_pos[0], tile_pos[1])
        self.equipment = []
        self.accoutrements = []
        self.abode = None
        self.facing = 'left'

    def loop(self, tv, _sprite):
        ppos = tv.tile_to_view(self.pos.to_tuple())
        self.rect.x = ppos[0]
        self.rect.y = ppos[1]

    def die(self, gameboard):
        """Play death animation, noises, whatever."""
        if hasattr(self, 'DEATH_SOUND'):
            sound.play_sound(self.DEATH_SOUND)
        if hasattr(self, 'DEATH_ANIMATION'):
            gameboard.animations.append(self.DEATH_ANIMATION(self.pos))
        self._game_death(gameboard)

    def _game_death(self, gameboard):
        # Call appropriate gameboard cleanup here.
        pass

    def move(self, state):
        """Given the game state, return a new position for the object"""
        # Default is not to move
        pass

    def set_pos(self, tile_pos):
        """Move an animal to the given tile_pos."""
        new_pos = Position(*tile_pos)
        self._fix_face(new_pos)
        self.pos = new_pos

    def _fix_face(self, facing_pos):
        """Set the face correctly"""
        if facing_pos.left_of(self.pos):
            self._set_image_facing('left')
        elif facing_pos.right_of(self.pos):
            self._set_image_facing('right')

    def _set_image_facing(self, facing):
        self.facing = facing
        if self.facing == 'left':
            self.setimage(self.image_left)
        elif self.facing == 'right':
            self.setimage(self.image_right)

    def equip(self, item):
        if equipment.is_equipment(item):
            self.equipment.append(item)
        elif equipment.is_accoutrement(item):
            self.accoutrements.append(item)
        self.redraw()

    def unequip(self, item):
        if equipment.is_equipment(item):
            self.equipment = [e for e in self.equipment if e != item]
        elif equipment.is_accoutrement(item):
            self.accoutrements = [e for e in self.accoutrements if e != item]
        self.redraw()

    def unequip_by_name(self, item_name):
        # only remove first match
        matches = [item for item in self.equipment + self.accoutrements if item.NAME == item_name]
        if matches:
            self.unequip(matches[0])

    def redraw(self):
        layers = [(self._image_left.copy(), self._image_right.copy(), 0)]
        if hasattr(self, 'EQUIPMENT_IMAGE_ATTRIBUTE'):
            for item in self.accoutrements + self.equipment:
                images = item.images(self.EQUIPMENT_IMAGE_ATTRIBUTE)
                if images:
                    layers.append(images)

        layers.sort(key=lambda l: l[2])

        # these always go on the bottom so that other layers don't get overwritten
        self.image_left = self._image_left.copy()
        self.image_right = self._image_right.copy()
        for l in layers:
            self.image_left.blit(l[0], (0,0))
            self.image_right.blit(l[1], (0,0))

        self._set_image_facing(self.facing)

    def weapons(self):
        return [e for e in self.equipment if equipment.is_weapon(e)]

    def armour(self):
        return [e for e in self.equipment if equipment.is_armour(e)]

    def covers(self, tile_pos):
        return tile_pos[0] == self.pos.x and tile_pos[1] == self.pos.y

    def outside(self):
        return self.abode is None

    def damage(self, gameboard):
        for a in self.armour():
            if not a.survive_damage():
                self.unequip(a)
            return True
        self.die(gameboard)
        return False

class Chicken(Animal):
    """A chicken"""

    EQUIPMENT_IMAGE_ATTRIBUTE = 'CHICKEN_IMAGE_FILE'
    DEATH_ANIMATION = animations.ChickenDeath
    DEATH_SOUND = 'kill-chicken.ogg'

    def __init__(self, pos):
        image_left = imagecache.load_image('sprites/chkn.png')
        image_right = imagecache.load_image('sprites/chkn.png',
                ("right_facing",))
        Animal.__init__(self, image_left, image_right, pos)
        self.eggs = []

    def _game_death(self, gameboard):
        gameboard.remove_chicken(self)

    def move(self, gameboard):
        """A free chicken will move away from other free chickens"""
        pass

    def lay(self):
        """See if the chicken lays an egg"""
        if not self.eggs:
            for x in range(random.randint(1, 4)):
                self.eggs.append(Egg(self.pos))
            self.equip(equipment.NestEgg())

    def remove_eggs(self):
        """Clean up the egg state"""
        self.eggs = []
        self.unequip_by_name("nestegg")

    def remove_one_egg(self):
        """Clean up the egg state"""
        self.eggs.pop()
        if not self.eggs:
            self.unequip_by_name("nestegg")

    def get_num_eggs(self):
        return len(self.eggs)

    def hatch(self, gameboard):
        """See if we have an egg to hatch"""
        if self.eggs:
            chick = self.eggs[0].hatch()
            if chick:
                # sell the remaining eggs
                # Remove hatched egg
                self.eggs.pop() 
                gameboard.eggs -= 1
                # Sell other eggs
                for egg in self.eggs[:]:
                    gameboard.sell_one_egg(self)
                self.remove_eggs() # clean up stale images, etc.
            return chick
        return None

    def _find_killable_fox(self, weapon, gameboard):
        """Choose a random fox within range of this weapon."""
        killable_foxes = []
        for fox in gameboard.foxes:
            if not visible(self, fox):
                continue
            if weapon.in_range(gameboard, self, fox):
                killable_foxes.append(fox)
        if not killable_foxes:
            return None
        return random.choice(killable_foxes)

    def attack(self, gameboard):
        """An armed chicken will attack a fox within range."""
        if not self.weapons():
            # Not going to take on a fox bare-winged.
            return
        # Choose the first weapon equipped.
        weapon = self.weapons()[0]
        fox = self._find_killable_fox(weapon, gameboard)
        if not fox:
            return
        self._fix_face(fox.pos)
        if weapon.hit(gameboard, self, fox):
            fox.damage(gameboard)

class Egg(Animal):
    """An egg"""

    def __init__(self, pos):
        image = imagecache.load_image('sprites/equip_egg.png')
        Animal.__init__(self, image, image, pos)
        self.timer = 2

    # Eggs don't move

    def hatch(self):
        self.timer -= 1
        if self.timer == 0:
            return Chicken(self.pos)
        return None

class Fox(Animal):
    """A fox"""

    STEALTH = 20
    IMAGE_FILE = 'sprites/fox.png'
    DEATH_ANIMATION = animations.FoxDeath
    DEATH_SOUND = 'kill-fox.ogg'

    costs = {
            # weighting for movement calculation
            'grassland' : 2,
            'woodland' : 1, # Try to keep to the woods if possible
            'broken fence' : 2,
            'fence' : 10,
            'guardtower' : 2, # We can pass under towers
            'henhouse' : 30, # Don't go into a henhouse unless we're going to
                             # catch a chicken there
            'hendominium' : 30,
            }

    def __init__(self, pos):
        image_left = imagecache.load_image(self.IMAGE_FILE)
        image_right = imagecache.load_image(self.IMAGE_FILE, ("right_facing",))
        Animal.__init__(self, image_left, image_right, pos)
        self.landmarks = [self.pos]
        self.hunting = True
        self.dig_pos = None
        self.tick = 0
        self.safe = False
        self.closest = None
        self.last_steps = []

    def _game_death(self, gameboard):
        gameboard.kill_fox(self)

    def _cost_tile(self, pos, gameboard):
        if gameboard.in_bounds(pos):
            this_tile = gameboard.tv.get(pos.to_tuple())
            cost = self.costs.get(tiles.TILE_MAP[this_tile], 100)
        else:
            cost = 100 # Out of bounds is expensive
        return cost

    def _cost_path(self, path, gameboard):
        """Calculate the cost of a path"""
        total = 0
        for pos in path:
            total += self._cost_tile(pos, gameboard)
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
        poss = [Position(x, y) for x in range(self.pos.x - 3, self.pos.x + 4)
                for y in range(self.pos.y - 3, self.pos.y + 4)
                if (x, y) != (0,0)]
        for start in poss:
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
                self.safe = True
                return self.pos
        return self._find_best_path_step(self.landmarks[-1], gameboard)

    def _find_path_to_chicken(self, gameboard):
        """Find the path to the closest chicken"""
        # Find the closest chicken
        min_dist = 999
        if self.closest not in gameboard.chickens:
            # Either no target, or someone ate it
            self.closest = None
            for chicken in gameboard.chickens:
                dist = chicken.pos.dist(self.pos)
                if chicken.abode:
                    dist += 10 # Prefer free-ranging chickens
                if dist < min_dist:
                    min_dist = dist
                    self.closest = chicken
        if not self.closest:
            # No more chickens, so leave
            self.hunting = False
            return self.pos
        if self.closest.pos == self.pos:
            # Caught a chicken
            self._catch_chicken(self.closest, gameboard)
            return self.pos
        return self._find_best_path_step(self.closest.pos, gameboard)

    def _catch_chicken(self, chicken, gameboard):
        """Catch a chicken"""
        chicken.damage(gameboard)
        self.closest = None
        self.hunting = False
        self.last_steps = [] # Forget history here

    def _update_pos(self, gameboard, new_pos):
        """Update the position, making sure we don't step on other foxes"""
        if new_pos == self.pos:
            # We're not moving, so we can skip all the checks
            return new_pos
        final_pos = new_pos
        blocked = final_pos in self.last_steps
        moves = [Position(x, y) for x in range(self.pos.x-1, self.pos.x + 2)
                for y in range(self.pos.y-1, self.pos.y + 2)
                if Position(x,y) != self.pos and \
                        Position(x, y) not in self.last_steps]
        for fox in gameboard.foxes:
            if fox is not self and fox.pos == final_pos:
                blocked = True
            if fox.pos in moves:
                moves.remove(fox.pos)
        if blocked:
            # find the cheapest point in moves to new_pos that's not blocked
            final_pos = None
            min_cost = 1000
            for poss in moves:
                cost = self._cost_tile(poss, gameboard)
                if cost < min_cost:
                    min_cost = cost
                    final_pos = poss
                if cost == min_cost and random.randint(0, 1) > 0:
                    # Add some randomness in this case
                    final_pos = poss
        if not final_pos:
            # No good choice, so stay put
            return self.pos
        if gameboard.in_bounds(final_pos):
            this_tile = gameboard.tv.get(final_pos.to_tuple())
        else:
            this_tile = tiles.REVERSE_TILE_MAP['woodland']
        if tiles.TILE_MAP[this_tile] == 'broken fence' and self.hunting:
            # We'll head back towards the holes we make/find
            self.landmarks.append(final_pos)
        elif tiles.TILE_MAP[this_tile] == 'fence' and not self.dig_pos:
            self._dig(gameboard, final_pos)
            return self.pos
        self.last_steps.append(final_pos)
        if len(self.last_steps) > 3:
            self.last_steps.pop(0)
        return final_pos

    def _dig(self, gameboard, dig_pos):
        """Setup dig parameters, to be overridden if needed"""
        self.tick = 5
        self.dig_pos = dig_pos

    def _make_hole(self, gameboard):
        """Make a hole in the fence"""
        gameboard.tv.set(self.dig_pos.to_tuple(), gameboard.BROKEN_FENCE)
        self.dig_pos = None

    def move(self, gameboard):
        """Foxes will aim to move towards the closest henhouse or free
           chicken"""
        if self.dig_pos:
            if self.tick:
                self.tick -= 1
                # We're still digging through the fence
                # Check the another fox hasn't dug a hole for us
                # We're too busy digging to notice if a hole appears nearby,
                # but we'll notice if the fence we're digging vanishes
                this_tile = gameboard.tv.get(self.dig_pos.to_tuple())
                if tiles.TILE_MAP[this_tile] == 'broken fence':
                    self.tick = 0 
                return
            else:
                # We've dug through the fence, so make a hole
                self._make_hole(gameboard)
            return 
        if self.hunting:
            desired_pos = self._find_path_to_chicken(gameboard)
        else:
            desired_pos = self._find_path_to_woodland(gameboard)
        final_pos = self._update_pos(gameboard, desired_pos)
        self._fix_face(final_pos)
        self.pos = final_pos

class NinjaFox(Fox):
    """Ninja foxes are hard to see"""

    STEALTH = 60
    IMAGE_FILE = 'sprites/ninja_fox.png'

class DemoFox(Fox):
    """Demolition Foxes destroy fences easily"""

    DIG_ANIMATION = animations.FenceExplosion
    IMAGE_FILE = 'sprites/sapper_fox.png'

    def __init__(self, pos):
        Fox.__init__(self, pos)
        self.costs['fence'] = 2 # We don't worry about fences

    def _dig(self, gameboard, dig_pos):
        """Setup dig parameters, to be overridden if needed"""
        self.tick = 0 # Costs us nothing to go through a fence.
        self.dig_pos = dig_pos
        gameboard.animations.append(self.DIG_ANIMATION(dig_pos))
        self._make_hole(gameboard)

class GreedyFox(Fox):
    """Greedy foxes eat more chickens"""

    def __init__(self, pos):
        Fox.__init__(self, pos)
        self.chickens_eaten = 0

    def _catch_chicken(self, chicken, gameboard):
        chicken.damage(gameboard)
        self.closest = None
        self.chickens_eaten += 1
        if self.chickens_eaten > 2:
            self.hunting = False
        self.last_steps = []

class Rinkhals(Fox):
    """The Rinkhals has eclectic tastes"""
    STEALTH = 80
    IMAGE_FILE = 'sprites/rinkhals.png'

    def _catch_chicken(self, chicken, gameboard):
        """The Rinkhals hunts for sport, catch and release style"""
        self.closest = None
        self.hunting = False
        self.last_steps = []

    def _make_hole(self, gameboard):
        """The Rinkhals eats fences"""
        gameboard.tv.set(self.dig_pos.to_tuple(), gameboard.GRASSLAND)
        self.dig_pos = None

    def damage(self, gameboard):
        """The Rinkhals is invincible!"""
        return True

def _get_vision_param(parameter, watcher):
    param = getattr(watcher, parameter)
    if watcher.abode:
        modifier = getattr(watcher.abode.building, 'MODIFY_'+parameter, lambda r: r)
        param = modifier(param)
    return param

def visible(watcher, watchee):
    vision_bonus = _get_vision_param('VISION_BONUS', watcher)
    range_penalty = _get_vision_param('VISION_RANGE_PENALTY', watcher)
    distance = watcher.pos.dist(watchee.pos) - 1
    roll = random.randint(1, 100)
    return roll > watchee.STEALTH - vision_bonus + range_penalty*distance
