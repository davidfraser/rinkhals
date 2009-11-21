"""Class for the various animals in the game"""

import random

from pgu.vid import Sprite

import imagecache
import tiles
from misc import Position
import sound
import equipment
import animations
import serializer
import constants

class Animal(Sprite, serializer.Simplifiable):
    """Base class for animals"""

    STEALTH = 0
    VISION_BONUS = 0
    VISION_RANGE_PENALTY = 10

    # sub-class must set this to the name of an image
    # file
    IMAGE_FILE = None

    SIMPLIFY = [
        'pos',
        'equipment',
        'accoutrements',
        'abode',
        'facing',
    ]

    def __init__(self, tile_pos):
        # load images
        self._image_left = imagecache.load_image(self.IMAGE_FILE)
        self._image_right = imagecache.load_image(self.IMAGE_FILE, ("right_facing",))
        # Create the animal somewhere far off screen
        Sprite.__init__(self, self._image_left, (-1000, -1000))
        self.image_left = self._image_left.copy()
        self.image_right = self._image_right.copy()
        if hasattr(tile_pos, 'to_tile_tuple'):
            self.pos = tile_pos
        else:
            self.pos = Position(tile_pos[0], tile_pos[1], 0)
        self.equipment = []
        self.accoutrements = []
        self.abode = None
        self.facing = 'left'

    def make(cls):
        """Override default Simplifiable object creation."""
        return cls((0, 0))
    make = classmethod(make)

    def unsimplify(cls, *args, **kwargs):
        """Override default Simplifiable unsimplification."""
        obj = super(Animal, cls).unsimplify(*args, **kwargs)
        obj.redraw()
        return obj
    unsimplify = classmethod(unsimplify)

    def loop(self, tv, _sprite):
        ppos = tv.tile_to_view(self.pos.to_tile_tuple())
        self.rect.x = ppos[0]
        self.rect.y = ppos[1]

    def die(self, gameboard):
        """Play death animation, noises, whatever."""
        if hasattr(self, 'DEATH_SOUND'):
            sound.play_sound(self.DEATH_SOUND)
        if hasattr(self, 'DEATH_ANIMATION'):
            self.DEATH_ANIMATION(gameboard.tv, self.pos.to_tile_tuple())
        self._game_death(gameboard)

    def _game_death(self, gameboard):
        # Call appropriate gameboard cleanup here.
        pass

    def move(self, state):
        """Given the game state, return a new position for the object"""
        # Default is not to move
        pass

    def attack(self, gameboard):
        """Given the game state, attack a suitable target"""
        # Default is not to attack
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
    IMAGE_FILE = 'sprites/chkn.png'

    SIMPLIFY = Animal.SIMPLIFY + ['eggs']

    def __init__(self, pos):
        Animal.__init__(self, pos)
        self.eggs = []

    def start_night(self, gameboard):
        self.lay(gameboard)
        self.reload_weapon()

    def start_day(self, gameboard):
        self.hatch(gameboard)

    def _game_death(self, gameboard):
        gameboard.remove_chicken(self)

    def move(self, gameboard):
        """A free chicken will wander around aimlessly"""
        pos_x, pos_y = self.pos.to_tile_tuple()
        surrounds = [Position(pos_x + dx, pos_y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]]
        pos_options = [pos for pos in surrounds if gameboard.in_bounds(pos) and gameboard.tv.get(pos.to_tile_tuple()) == gameboard.GRASSLAND and not gameboard.get_outside_chicken(pos.to_tile_tuple())] + [self.pos]
        self.pos = pos_options[random.randint(0, len(pos_options)-1)]

    def chop(self, gameboard):
        pos_x, pos_y = self.pos.to_tile_tuple()
        surrounds = [Position(pos_x + dx, pos_y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]]
        tree_options = [pos for pos in surrounds if gameboard.in_bounds(pos) and gameboard.tv.get(pos.to_tile_tuple()) == gameboard.WOODLAND]
        if tree_options:
            num_trees_to_cut = random.randint(1, len(tree_options))
            trees_to_cut = random.sample(tree_options, num_trees_to_cut)
            for tree_pos in trees_to_cut:
                gameboard.add_wood(5)
                gameboard.tv.set(tree_pos.to_tile_tuple(), gameboard.GRASSLAND)

    def lay(self, gameboard):
        """See if the chicken lays an egg"""
        if self.abode and self.abode.building.HENHOUSE:
            if not self.eggs:
                for x in range(random.randint(1, 4)):
                    self.eggs.append(Egg(self.pos))
                self.equip(equipment.NestEgg())
            gameboard.eggs += self.get_num_eggs()

    def remove_eggs(self):
        """Clean up the egg state"""
        self.eggs = []
        self.unequip_by_name("Nestegg")

    def remove_one_egg(self):
        """Clean up the egg state"""
        self.eggs.pop()
        if not self.eggs:
            self.unequip_by_name("Nestegg")

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
                gameboard.place_hatched_chicken(chick, self.abode.building)

    def _find_killable_fox(self, weapon, gameboard):
        """Choose a random fox within range of this weapon."""
        killable_foxes = []
        for fox in gameboard.foxes:
            if not visible(self, fox, gameboard):
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

    def reload_weapon(self):
        """If we have a weapon that takes ammunition, reload it."""
        for weapon in self.weapons():
            weapon.refresh_ammo()

class Egg(Animal):
    """An egg"""

    IMAGE_FILE = 'sprites/equip_egg.png'

    SIMPLIFY = Animal.SIMPLIFY + ['timer']

    def __init__(self, pos):
        Animal.__init__(self, pos)
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
    CONFIG_NAME = 'fox'

    costs = {
            # weighting for movement calculation
            'grassland' : 2,
            'woodland' : 1, # Try to keep to the woods if possible
            'broken fence' : 2,
            'fence' : 25,
            'guardtower' : 2, # We can pass under towers
            'henhouse' : 30, # Don't go into a henhouse unless we're going to
                             # catch a chicken there
            'hendominium' : 30,
            }

    def __init__(self, pos):
        Animal.__init__(self, pos)
        self.landmarks = [self.pos]
        self.hunting = True
        self.dig_pos = None
        self.tick = 0
        self.safe = False
        self.closest = None
        self.last_steps = []
        # Foxes don't occupy places in the same way chickens do, but they
        # can still be inside
        self.building = None

    def outside(self):
        return self.building is None

    def _game_death(self, gameboard):
        gameboard.kill_fox(self)

    def _cost_tile(self, pos, gameboard):
        if gameboard.in_bounds(pos):
            this_tile = gameboard.tv.get(pos.to_tile_tuple())
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
        return start_pos.intermediate_positions(final_pos)

    def _find_best_path_step(self, final_pos, gameboard):
        """Find the cheapest path to final_pos, and return the next step
           along the path."""
        # We calculate the cost of the direct path
        if final_pos.z < self.pos.z:
            # We need to try heading down.
            return Position(self.pos.x, self.pos.y, self.pos.z - 1)
        if final_pos.x == self.pos.x and final_pos.y == self.pos.y and \
                final_pos.z > self.pos.z:
            # We try heading up
            return Position(self.pos.x, self.pos.y, self.pos.z + 1)
        cur_dist = final_pos.dist(self.pos)
        if cur_dist < 2:
            # We're right ontop of our target, so just go there
            return final_pos
        # Find the cheapest spot close to us that moves us closer to the target
        neighbours = [Position(self.pos.x + x, self.pos.y + y, self.pos.z) for
                x in range(-1, 2) for y in range(-1, 2) if (x, y) != (0, 0)]
        best_pos = self.pos
        min_cost = 1000
        min_dist = cur_dist
        for point in neighbours:
            dist = point.dist(final_pos)
            if dist < cur_dist:
                cost = self._cost_tile(point, gameboard)
                if cost < min_cost or (min_cost == cost and dist < min_dist):
                    # Prefer closest of equal cost points
                    min_dist = dist
                    min_cost = cost
                    best = point
        if min_cost < 20 or not gameboard.in_bounds(self.pos):
            # If we're not on the gameboard yet, there's no point in looking
            # for an optimal path.
            return best
        # Else expensive step, so think further
        direct_path = self._gen_path(self.pos, final_pos)
        min_cost = self._cost_path(direct_path, gameboard)
        min_path = direct_path
        # is there a point nearby that gives us a cheaper direct path?
        # This is delibrately not finding the optimal path, as I don't
        # want the foxes to be too intelligent, although the implementation
        # isn't well optimised yet
        # FIXME: Currently, this introduces loops, but the memory kind
        # avoids that.  Fixing this is the next goal.
        poss = [Position(self.pos.x + x, self.pos.y + y, self.pos.z) for
                x in range(-3, 4) for y in range(-3, 4) if (x, y) != (0, 0)]
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
        if not gameboard.in_bounds(self.pos) and not self.hunting:
            # Safely out of sight
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
                    dist += 5 # Prefer free-ranging chickens
                if len(chicken.weapons()) > 0:
                    dist += 5 # Prefer unarmed chickens
                if dist < min_dist:
                    min_dist = dist
                    self.closest = chicken
        if not self.closest:
            # No more chickens, so leave
            self.hunting = False
            return self.pos
        if self.closest.pos == self.pos:
            # No need to move
            return self.pos
        if self.closest.pos.to_tile_tuple() == self.pos.to_tile_tuple():
            # Only differ in z, so next step is in z
            if self.closest.pos.z < self.pos.z:
                new_z = self.pos.z - 1
            else:
                new_z = self.pos.z + 1
            return Position(self.pos.x, self.pos.y, new_z)
        return self._find_best_path_step(self.closest.pos, gameboard)

    def attack(self, gameboard):
        """Attack a chicken"""
        chicken = gameboard.get_animal_at_pos(self.pos, 'chicken')
        if chicken:
            # Always attack a chicken we step on, even if not hunting
            self._catch_chicken(chicken, gameboard)

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
        blocked = gameboard.get_animal_at_pos(new_pos, 'fox') is not None
        if not blocked and new_pos.z == self.pos.z:
            # We're only worried about loops when not on a ladder
            blocked = new_pos in self.last_steps
        final_pos = new_pos
        if blocked:
            if new_pos.z != self.pos.z:
                # We can only move up and down a ladder
                moves = [Position(self.pos.x, self.pos.y, z) for z
                        in range(self.pos.z-1, self.pos.z + 2) if z >= 0]
            else:
                moves = [Position(x, y) for x in range(self.pos.x-1, self.pos.x + 2)
                        for y in range(self.pos.y-1, self.pos.y + 2)
                        if Position(x,y) != self.pos and
                        Position(x, y) not in self.last_steps and
                        self.pos.z == 0]
            # find the cheapest point in moves that's not blocked
            final_pos = None
            min_cost = 1000
            for poss in moves:
                if gameboard.get_animal_at_pos(poss, 'fox'):
                    continue # blocked
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
            this_tile = gameboard.tv.get(final_pos.to_tile_tuple())
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
        fence = gameboard.get_building(self.dig_pos.to_tile_tuple())
        # Another fox could have made the same hole this turn
        if fence:
            fence.damage(gameboard.tv)
        self.dig_pos = None

    def move(self, gameboard):
        """Foxes will aim to move towards the closest henhouse or free
           chicken"""
        if self.safe:
            # We're safe, so do nothing
            return
        elif self.dig_pos:
            if self.tick:
                self.tick -= 1
                # We're still digging through the fence
                # Check the another fox hasn't dug a hole for us
                # We're too busy digging to notice if a hole appears nearby,
                # but we'll notice if the fence we're digging vanishes
                this_tile = gameboard.tv.get(self.dig_pos.to_tile_tuple())
                if tiles.TILE_MAP[this_tile] == 'broken fence':
                    self.tick = 0
            else:
                # We've dug through the fence, so make a hole
                self._make_hole(gameboard)
            return
        elif self.hunting:
            desired_pos = self._find_path_to_chicken(gameboard)
        else:
            desired_pos = self._find_path_to_woodland(gameboard)
        final_pos = self._update_pos(gameboard, desired_pos)
        self._fix_face(final_pos)
        self.pos = final_pos
        change_visible = False
        # See if we're entering/leaving a building
        building = gameboard.get_building(final_pos.to_tile_tuple())
        if building and self.outside():
            # Check if we need to enter
            if self.closest and not self.closest.outside() and \
                    self.closest.abode.building is building:
                building.add_predator(self)
                change_visible = True
        elif self.building and final_pos.z == 0:
            # can only leave from the ground floor
            if building == self.building:
                # Check if we need to leave the building
                if not self.hunting or (self.closest and
                        self.closest.abode.building is not building):
                    self.building.remove_predator(self)
                    change_visible = True
            else:
                # we've moved away from the building we were in
                self.building.remove_predator(self)
                change_visible = True
        if change_visible:
            gameboard.set_visibility(self)


class NinjaFox(Fox):
    """Ninja foxes are hard to see"""

    STEALTH = 60
    IMAGE_FILE = 'sprites/ninja_fox.png'
    CONFIG_NAME = 'ninja fox'

class DemoFox(Fox):
    """Demolition Foxes destroy fences easily"""

    DIG_ANIMATION = animations.FenceExplosion
    IMAGE_FILE = 'sprites/sapper_fox.png'
    CONFIG_NAME = 'sapper fox'

    costs = Fox.costs.copy()
    costs['fence'] = 2

    def _dig(self, gameboard, dig_pos):
        """Setup dig parameters, to be overridden if needed"""
        self.tick = 0 # Costs us nothing to go through a fence.
        self.dig_pos = dig_pos
        self.DIG_ANIMATION(gameboard.tv, dig_pos.to_tile_tuple())
        self._make_hole(gameboard)

class GreedyFox(Fox):
    """Greedy foxes eat more chickens"""
    CONFIG_NAME = 'greedy fox'

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
    CONFIG_NAME = 'rinkhals'

    def _catch_chicken(self, chicken, gameboard):
        """The Rinkhals hunts for sport, catch and release style"""
        self.closest = None
        self.hunting = False
        self.last_steps = []

    def _make_hole(self, gameboard):
        """The Rinkhals eats fences"""
        fence = gameboard.get_building(self.dig_pos.to_tile_tuple())
        if fence:
            fence.remove(gameboard.tv)
            gameboard.remove_building(fence)
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

def visible(watcher, watchee, gameboard):
    vision_bonus = _get_vision_param('VISION_BONUS', watcher)
    range_penalty = _get_vision_param('VISION_RANGE_PENALTY', watcher)
    positions = watcher.pos.intermediate_positions(watchee.pos)
    for pos in positions:
        building = gameboard.get_building(pos.to_tile_tuple())
        # This allows chickens to fire across GuardTowers and Fences.
        if building and building.BLOCKS_VISION and not (watcher in building.occupants()):
            return False
    distance = watcher.pos.dist(watchee.pos) - 1
    # Intervening forests get in the way a bit.
    woods = len([pos for pos in positions if gameboard.tv.get(pos.to_tile_tuple()) == gameboard.WOODLAND])
    roll = random.randint(1, 100)
    return roll > watchee.STEALTH - vision_bonus + range_penalty*distance + constants.WOODLAND_CONCEALMENT*woods

# These don't have to add up to 100, but it's easier to think
# about them if they do.
DEFAULT_FOX_WEIGHTINGS = (
    (Fox, 59),
    (GreedyFox, 30),
    (NinjaFox, 5),
    (DemoFox, 5),
    (Rinkhals, 1),
    )

