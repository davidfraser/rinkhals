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


NEIGHBOUR_4 = [Position(-1, 0), Position(1, 0), Position(0, 1), Position(0, -1)]


NEIGHBOUR_8 = [Position(-1, 0), Position(1, 0), Position(0, 1), Position(0, -1),
        Position(1, 1), Position(1, -1), Position(-1, 1), Position(-1, -1)]


TILE_FENCE = tiles.REVERSE_TILE_MAP['fence']

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
        'gameboard',
    ]

    def __init__(self, tile_pos, gameboard):
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
        self.gameboard = gameboard

    @classmethod
    def make(cls):
        """Override default Simplifiable object creation."""
        return cls((0, 0), None)

    @classmethod
    def unsimplify(cls, *args, **kwargs):
        """Override default Simplifiable unsimplification."""
        obj = super(Animal, cls).unsimplify(*args, **kwargs)
        obj.redraw()
        return obj

    def loop(self, tv, _sprite):
        ppos = tv.tile_to_view(self.pos.to_tile_tuple())
        self.rect.x = ppos[0]
        self.rect.y = ppos[1]

    def die(self):
        """Play death animation, noises, whatever."""
        if hasattr(self, 'DEATH_SOUND'):
            sound.play_sound(self.DEATH_SOUND)
        if hasattr(self, 'DEATH_ANIMATION'):
            self.DEATH_ANIMATION(self.gameboard.tv, self.pos.to_tile_tuple())
        self._game_death()

    def _game_death(self):
        # Call appropriate gameboard cleanup here.
        pass

    def move(self):
        """Return a new position for the object"""
        # Default is not to move
        pass

    def attack(self):
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

    def surveillance_equipment(self):
        return [e for e in self.equipment if equipment.is_surveillance_equipment(e)]

    def armour(self):
        return [e for e in self.equipment if equipment.is_armour(e)]

    def covers(self, tile_pos):
        return tile_pos[0] == self.pos.x and tile_pos[1] == self.pos.y

    def outside(self):
        return self.abode is None

    def damage(self):
        for a in self.armour():
            if not a.survive_damage():
                self.unequip(a)
            return True
        self.die()
        return False

class Chicken(Animal):
    """A chicken"""

    EQUIPMENT_IMAGE_ATTRIBUTE = 'ANIMAL_IMAGE_FILE'
    DEATH_ANIMATION = animations.ChickenDeath
    DEATH_SOUND = 'kill-chicken.ogg'
    IMAGE_FILE = 'sprites/chkn.png'

    SIMPLIFY = Animal.SIMPLIFY + ['eggs']

    def __init__(self, pos, gameboard):
        Animal.__init__(self, pos, gameboard)
        self.eggs = []

    def start_night(self):
        self.lay()
        self.reload_weapon()

    def start_day(self):
        self.hatch()

    def _game_death(self):
        self.gameboard.remove_chicken(self)

    def move(self):
        """A free chicken will wander around aimlessly"""
        pos_x, pos_y = self.pos.to_tile_tuple()
        surrounds = [Position(pos_x + dx, pos_y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]]
        pos_options = [pos for pos in surrounds if self.gameboard.in_bounds(pos) and self.gameboard.tv.get(pos.to_tile_tuple()) == self.gameboard.GRASSLAND and not self.gameboard.get_outside_chicken(pos.to_tile_tuple())] + [self.pos]
        self.pos = pos_options[random.randint(0, len(pos_options)-1)]

    def has_axe(self):
        return bool([e for e in self.weapons() if e.TYPE == "AXE"])

    def chop(self):
        if self.has_axe():
            pos_x, pos_y = self.pos.to_tile_tuple()
            surrounds = [Position(pos_x + dx, pos_y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]]
            tree_options = [pos for pos in surrounds if self.gameboard.in_bounds(pos) and self.gameboard.is_woodland_tile(pos)]
            if tree_options:
                num_trees_to_cut = random.randint(1, len(tree_options))
                trees_to_cut = random.sample(tree_options, num_trees_to_cut)
                for tree_pos in trees_to_cut:
                    self.gameboard.add_wood(5)
                    self.gameboard.tv.set(tree_pos.to_tile_tuple(), self.gameboard.GRASSLAND)

    def lay(self):
        """See if the chicken lays an egg"""
        if self.abode and self.abode.building.HENHOUSE:
            # TODO: Find a cleaner way to do this
            fertilised = False
            for bird in self.abode.building.occupants():
                if getattr(bird, 'ROOSTER', None):
                    fertilised = True
            if not self.eggs:
                for x in range(random.randint(1, 4)):
                    self.eggs.append(Egg(self.pos, self.gameboard, fertilised=fertilised))
                self.equip(equipment.NestEgg())
            self.gameboard.eggs += self.get_num_eggs()

    def remove_eggs(self):
        """Clean up the egg state"""
        self.gameboard.remove_eggs(len(self.eggs))
        self.eggs = []
        self.unequip_by_name("Nestegg")

    def remove_one_egg(self):
        """Clean up the egg state"""
        self.eggs.pop()
        self.gameboard.remove_eggs(1)
        if not self.eggs:
            self.unequip_by_name("Nestegg")

    def get_num_eggs(self):
        return len(self.eggs)

    def hatch(self):
        """See if we have an egg to hatch"""
        if self.eggs:
            chick = self.eggs[0].hatch()
            if chick:
                # sell the remaining eggs
                # Remove hatched egg
                self.remove_one_egg()
                # Sell other eggs
                for egg in self.eggs[:]:
                    self.gameboard.sell_one_egg(self)
                self.remove_eggs() # clean up stale images, etc.
                self.gameboard.place_hatched_chicken(chick, self.abode.building)

    def _find_killable_fox(self, weapon):
        """Choose a random fox within range of this weapon."""
        killable_foxes = []
        for fox in self.gameboard.foxes:
            if not weapon.in_range(self.gameboard, self, fox):
                continue
            if visible(self, fox, self.gameboard):
                killable_foxes.append(fox)
        if not killable_foxes:
            return None
        return random.choice(killable_foxes)

    def attack(self):
        """An armed chicken will attack a fox within range."""
        if not self.weapons():
            # Not going to take on a fox bare-winged.
            return
        # Choose the first weapon equipped.
        weapon = self.weapons()[0]
        fox = self._find_killable_fox(weapon)
        if not fox:
            return
        self._fix_face(fox.pos)
        if weapon.hit(self.gameboard, self, fox):
            fox.damage()

    def reload_weapon(self):
        """If we have a weapon that takes ammunition, reload it."""
        for weapon in self.weapons():
            weapon.refresh_ammo()


class Rooster(Chicken):
    """A rooster"""

    IMAGE_FILE = 'sprites/rooster.png'
    ROOSTER = True

    AGGRESSION = 50

    def lay(self):
        # Roosters don't lay eggs.
        pass

    def start_night(self):
        Chicken.start_night(self)
        self._manly_fight()

    def _manly_fight(self):
        if self.abode:
            for rival in [occ for occ in self.abode.building.occupants()
                          if getattr(occ, 'ROOSTER', False)]:
                if random.randint(1, 100) <= self.AGGRESSION:
                    rival.damage()


class Egg(Animal):
    """An egg"""

    IMAGE_FILE = 'sprites/equip_egg.png'

    SIMPLIFY = Animal.SIMPLIFY + ['timer', 'fertilised']

    def __init__(self, pos, gameboard, fertilised=False):
        Animal.__init__(self, pos, gameboard)
        self.fertilised = fertilised
        self.timer = 2

    # Eggs don't move

    def hatch(self):
        self.timer -= 1
        if self.timer == 0 and self.fertilised:
            return random.choice([Chicken, Rooster])(self.pos, self.gameboard)
        return None


class Fox(Animal):
    """A fox"""

    STEALTH = 20
    IMAGE_FILE = 'sprites/fox.png'
    EQUIPMENT_IMAGE_ATTRIBUTE = 'ANIMAL_IMAGE_FILE'
    DEATH_ANIMATION = animations.FoxDeath
    DEATH_SOUND = 'kill-fox.ogg'
    CONFIG_NAME = 'fox'

    costs = {
            # weighting for movement calculation
            'grassland' : 2,
            'woodland' : 1, # Try to keep to the woods if possible
            'broken fence' : 1,
            'fence' : 25,
            'guardtower' : 2, # We can pass under towers
            'henhouse' : 30, # Don't go into a henhouse unless we're going to
                             # catch a chicken there
            'hendominium' : 30,
            }

    def __init__(self, pos, gameboard):
        Animal.__init__(self, pos, gameboard)
        self.start_pos = self.pos
        self.target = None
        self.hunting = True
        self.dig_pos = None
        self.tick = 0
        self.safe = False
        self.closest = None
        # Foxes don't occupy places in the same way chickens do, but they
        # can still be inside
        self.building = None
        self._last_steps = []
        self.path = []

    def outside(self):
        return self.building is None

    def _game_death(self):
        self.gameboard.kill_fox(self)

    def _cost_tile(self, pos):
        if self.gameboard.in_bounds(pos):
            this_tile = self.gameboard.tv.get(pos.to_tile_tuple())
            cost = self.costs.get(tiles.TILE_MAP[this_tile], 100)
        else:
            cost = 100 # Out of bounds is expensive
        return cost

    def _is_fence(self, pos):
        if self.gameboard.in_bounds(pos):
            this_tile = self.gameboard.tv.get(pos.to_tile_tuple())
            return this_tile == TILE_FENCE
        return False

    def _check_steps(self, step, border_func, end_func, max_steps):
        steps = 0
        cur_pos = self.pos
        path = []
        while steps < max_steps:
            if not border_func(cur_pos):
                # Not walking the edge
                return None
            path.append(cur_pos)
            if end_func(cur_pos):
                # is there an 8-NEIGHBOUR that also satisfies end_func and is
                # closer to target
                dist = self.target.dist(cur_pos)
                fin_pos = None
                for pos in [cur_pos + x for x in NEIGHBOUR_8]:
                    if pos in path:
                        continue
                    if end_func(pos) and self.target.dist(pos) < dist:
                        fin_pos = pos
                        dist = self.target.dist(pos)
                if fin_pos:
                    path.append(fin_pos)
                return path
            steps += 1
            cur_pos = cur_pos + step
        return None

    def _search_for_path(self, border_func, end_func, max_steps):
        paths = [None] * 4
        paths[0] = self._check_steps(Position(-1, 0), border_func, end_func, max_steps)
        paths[1] = self._check_steps(Position(0, -1), border_func, end_func, max_steps)
        paths[2] = self._check_steps(Position(1, 0), border_func, end_func, max_steps)
        paths[3] = self._check_steps(Position(0, 1), border_func, end_func, max_steps)
        cands = [x for x in paths if x is not None]
        if not cands:
            return None
        elif len(cands) == 1:
            return cands[0][1:]
        # take the end point closest to our target
        final_path = cands[0]
        min_dist = final_path[-1].dist(self.target)
        for this_path in cands[1:]:
            dist = this_path[-1].dist(self.target)
            if dist < min_dist:
                min_dist = dist
                final_path = this_path
            elif dist == min_dist and random.randint(0, 1) == 0:
                final_path = this_path
        return final_path[1:] # path's include self.pos

    def _find_nearest_corner(self):
        """Find the nearest corner of the building"""
        COST_MARGIN = 25
        def border(pos):
            cost = self._cost_tile(pos)
            if cost >= COST_MARGIN:
                return False # in building isn't border
            for tpos in [pos + step for step in NEIGHBOUR_8]:
                if self.gameboard.in_bounds(tpos):
                    cost = self._cost_tile(tpos)
                    if cost >= COST_MARGIN:
                        return True
            return False

        def corner(pos):
            # A corner is not 4-connected to a building
            if not border(pos):
                return False
            for tpos in [pos + step for step in NEIGHBOUR_4]:
                if self.gameboard.in_bounds(tpos):
                    cost = self._cost_tile(tpos)
                    if cost >= COST_MARGIN:
                        return False
            return True

        return self._search_for_path(border, corner, 6)

    def _find_fence_gap(self):
        # We search for a gap in the fence
        # we know we are next to fence. A gap in the fence is
        # a point that borders the fence where the fence is not
        # 4-connected

        COST_MARGIN = 25

        def border(pos):
            if self._is_fence(pos) or self._cost_tile(pos) >= COST_MARGIN:
                return False
            for tpos in [pos + step for step in NEIGHBOUR_8]:
                if self._is_fence(tpos) or self._cost_tile(tpos) >= COST_MARGIN:
                    return True
            return False

        def is_gap(pos):
            # A gap neighbours only fence tiles which has < 2 4-neighbours
            if self._is_fence(pos):
                return False
            fence_neighbours = [0]
            for tpos in [pos + step for step in NEIGHBOUR_8]:
                if self._is_fence(tpos):
                    connections = 0
                    for fpos in [tpos + step for step in NEIGHBOUR_4]:
                        if self.gameboard.in_bounds(fpos):
                            if self._is_fence(fpos) or self._cost_tile(tpos) >= COST_MARGIN:
                                # Expensive building is considered fence
                                connections += 1
                        else:
                            # Fence connecting to out of bounds counts as fence
                            connections += 1
                    fence_neighbours.append(connections)
            return max(fence_neighbours) < 2

        return self._search_for_path(border, is_gap, 7)

    def _find_min_cost_neighbour(self, target):
        """Find the minimum cost neighbour that's closer to target"""
        cur_dist = target.dist(self.pos)
        neighbours = [self.pos + step for step in NEIGHBOUR_8]
        min_cost = 1000
        min_dist = cur_dist
        best = self.pos
        for point in neighbours:
            if point in self._last_steps:
                continue
            dist = point.dist(target)
            if dist <= min_dist:
                cost = self._cost_tile(point)
                if cost < min_cost or (min_cost == cost and dist < min_dist):
                    # Prefer closest of equal cost points
                    min_dist = dist
                    min_cost = cost
                    best = point
                elif min_cost == cost and random.randint(0, 1) == 0:
                    # Be slightly non-deterministic when presented with
                    # equal choices
                    best = point
        return best, min_cost

    def _find_best_path_step(self):
        """Find the cheapest path to final_pos, and return the next step
           along the path."""
        if self.path:
            next_step = self.path.pop(0)
            if next_step.dist(self.pos) < 2:
                return next_step
            else:
                # Been bounced off the path
                self.path = []
        new_pos = None
        if self.target.z < self.pos.z:
            # We need to try heading down.
            new_pos = Position(self.pos.x, self.pos.y, self.pos.z - 1)
        if self.target.x == self.pos.x and self.target.y == self.pos.y and \
                self.target.z > self.pos.z:
            # We try heading up
            new_pos = Position(self.pos.x, self.pos.y, self.pos.z + 1)
        if new_pos:
            if new_pos in self._last_steps:
                # ladder, so we allow backtracking
                self._last_steps.remove(new_pos)
            return new_pos
        cur_dist = self.target.dist(self.pos)
        if cur_dist < 2:
            # We're right ontop of our target, so just go there
            return self.target
        # Find the cheapest spot close to us that moves us closer to the target
        best, min_cost = self._find_min_cost_neighbour(self.target)
        if min_cost < 20 or not self.gameboard.in_bounds(self.pos) \
                or not self.gameboard.in_bounds(best):
            # If we're not on the gameboard yet, there's no point in looking
            # for an optimal path.
            return best
        # Else expensive step, so think further
        if self._is_fence(best):
            path = self._find_fence_gap()
        elif min_cost == 30:
            # building
            path = self._find_nearest_corner()
        else:
            # We're looping
            self._last_steps = []
            return self.pos
        if path:
            self.path = path[1:] # exclude 1st step
            return path[0]
        return best

    def _calc_next_move(self):
        """Find the path to the target"""
        if self.hunting:
            # Check if we need to update our idea of a target
            if not self.closest or self.closest not in self.gameboard.chickens:
                # Either no target, or someone ate it
                self._select_prey()
            elif not self.target:
                self.target = self.closest.pos
        if not self.target:
            self.target = self.start_pos
            self._last_steps = []
        if self.target == self.pos:
            # No need to move, but we will need to update the target
            self.target = None
            return self.pos
        if self.target.to_tile_tuple() == self.pos.to_tile_tuple():
            # Only differ in z, so next step is in z
            if self.target.z < self.pos.z:
                new_z = self.pos.z - 1
            else:
                new_z = self.pos.z + 1
            return Position(self.pos.x, self.pos.y, new_z)
        return self._find_best_path_step()

    def _calculate_dist(self, chicken):
        """Calculate the distance to the chicken"""
        dist = chicken.pos.dist(self.pos)
        if chicken.abode:
            dist += 5 # Prefer free-ranging chickens
        if len(chicken.weapons()) > 0:
            dist += 5 # Prefer unarmed chickens
        return dist

    def _select_prey(self):
        min_dist = 999
        self.closest = None
        for chicken in self.gameboard.chickens:
            dist = self._calculate_dist(chicken)
            if dist < min_dist:
                min_dist = dist
                self.closest = chicken
                self.target = chicken.pos
        if not self.closest:
            # No more chickens, so leave
            self.hunting = False
            self.target = self.start_pos
            return self.pos

    def attack(self):
        """Attack a chicken"""
        chicken = self.gameboard.get_animal_at_pos(self.pos, 'chicken')
        if chicken:
            # Always attack a chicken we step on, even if not hunting
            self._catch_chicken(chicken)

    def _catch_chicken(self, chicken):
        """Catch a chicken"""
        chicken.damage()
        self.closest = None
        self.hunting = False
        self.target = self.start_pos
        self._last_steps = []

    def _update_pos(self, new_pos):
        """Update the position, making sure we don't step on other foxes"""
        if not self.hunting and not self.gameboard.in_bounds(self.pos):
            self.safe = True
            return self.pos
        if new_pos == self.pos:
            # We're not moving, so we can skip all the checks
            return new_pos
        blocked = self.gameboard.get_animal_at_pos(new_pos, 'fox') is not None
        final_pos = new_pos
        if blocked:
            if new_pos.z != self.pos.z or self.pos.z != 0:
                # We can only move up and down a ladder
                moves = [Position(self.pos.x, self.pos.y, z) for z
                        in range(self.pos.z-1, self.pos.z + 2) if z >= 0]
            else:
                moves = [self.pos + step for step in NEIGHBOUR_8]
            # find the cheapest point in moves that's not blocked
            final_pos = None
            min_cost = 1000
            for poss in moves:
                if self.gameboard.get_animal_at_pos(poss, 'fox'):
                    continue # blocked
                cost = self._cost_tile(poss)
                if cost < min_cost:
                    min_cost = cost
                    final_pos = poss
                if cost == min_cost and random.randint(0, 1) > 0:
                    # Add some randomness in this case
                    final_pos = poss
        if not final_pos:
            # No good choice, so stay put
            return self.pos
        if self._is_fence(final_pos) and not self.dig_pos:
            return self._dig(final_pos)
        self._last_steps.append(final_pos)
        if len(self._last_steps) > 6:
            self._last_steps.pop(0)
        return final_pos

    def _dig(self, dig_pos):
        """Setup dig parameters, to be overridden if needed"""
        self.tick = 5
        self.dig_pos = dig_pos
        return self.pos

    def _make_hole(self):
        """Make a hole in the fence"""
        fence = self.gameboard.get_building(self.dig_pos.to_tile_tuple())
        # Another fox could have made the same hole this turn
        if fence:
            fence.damage()
        self.dig_pos = None

    def move(self):
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
                if not self._is_fence(self.dig_pos):
                    self.tick = 0
            else:
                # We've dug through the fence, so make a hole
                self._make_hole()
            return
        desired_pos = self._calc_next_move()
        final_pos = self._update_pos(desired_pos)
        self._fix_face(final_pos)
        self.pos = final_pos
        change_visible = False
        # See if we're entering/leaving a building
        building = self.gameboard.get_building(final_pos.to_tile_tuple())
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
                if not self.hunting or (self.closest and self.closest.abode
                        and self.closest.abode.building is not building):
                    self.building.remove_predator(self)
                    change_visible = True
            else:
                # we've moved away from the building we were in
                self.building.remove_predator(self)
                change_visible = True
        if change_visible:
            self.gameboard.set_visibility(self)


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

    def _dig(self, dig_pos):
        """Setup dig parameters, to be overridden if needed"""
        self.tick = 0 # Costs us nothing to go through a fence.
        self.dig_pos = dig_pos
        self.DIG_ANIMATION(self.gameboard.tv, dig_pos.to_tile_tuple())
        self._make_hole()
        return self.pos

class GreedyFox(Fox):
    """Greedy foxes eat more chickens"""
    CONFIG_NAME = 'greedy fox'
    IMAGE_FILE = 'sprites/greedy_fox.png'

    def __init__(self, pos, gameboard):
        Fox.__init__(self, pos, gameboard)
        self.chickens_eaten = 0
        self.last_chicken = None

    def _catch_chicken(self, chicken):
        chicken.damage()
        self.last_chicken = self.closest
        self.closest = None
        self.chickens_eaten += 1
        if self.chickens_eaten > 2:
            self.hunting = False
            self.target = self.start_pos
            self._last_steps = []
        else:
            self._select_prey() # select new target

    def _calculate_dist(self, chicken):
        """Calculate the distance to the chicken"""
        dist = super(GreedyFox, self)._calculate_dist(chicken)
        if self.last_chicken and self.last_chicken is chicken:
            # We hurt our teeth, only attack the same chicken if it's the
            # only one nearby
            dist += 15
        return dist

class ShieldFox(Fox):
    """The Shield Fox has a shield, so is harder to damage"""
    CONFIG_NAME = 'shield fox'

    def __init__(self, pos, gameboard):
        Fox.__init__(self, pos, gameboard)
        self.equip(equipment.Shield())

class RobberFox(Fox):
    CONFIG_NAME = 'robber fox'
    IMAGE_FILE = 'sprites/robber_fox.png'
    STEALTH = 40

    def __init__(self, pos, gameboard):
        Fox.__init__(self, pos, gameboard)
        self.chickens_robbed = 0
        self.hungry = False
        self.last_chicken = None

    def _catch_chicken(self, chicken):
        """Catch a chicken"""
        if chicken.equipment:
            e = random.choice(chicken.equipment)
            chicken.unequip(e)
            self.equip(e)
            self.hungry = True
        elif self.hungry:
            chicken.damage()
        self.last_chicken = self.closest
        self.closest = None
        self.chickens_robbed += 1
        if self.chickens_robbed > 2:
            self.hunting = False
            self.target = self.start_pos
            self._last_steps = []
        else:
            self._select_prey() # select new target

    def _calculate_dist(self, chicken):
        """Calculate the distance to the chicken"""
        dist = chicken.pos.dist(self.pos)
        if chicken.abode:
            dist += 5 # Prefer free-ranging chickens
        if not self.hungry and not chicken.equipment:
            dist += 1000 # Ignore chickens with nothing to steal
        if len(chicken.weapons()) > 0:
            dist += 5 # Prefer unarmed chickens
        if self.last_chicken and self.last_chicken is chicken:
            # That chicken may be suspicious of us; careful of robbing it again
            dist += 10
        return dist

class Rinkhals(Fox):
    """The Rinkhals has eclectic tastes"""
    STEALTH = 80
    IMAGE_FILE = 'sprites/rinkhals.png'
    CONFIG_NAME = 'rinkhals'

    costs = Fox.costs.copy()
    costs['fence'] = 2

    def _calculate_dist(self, chicken):
        """The Rinkhals eats eggs, so tweak distance accordingly"""
        dist = chicken.pos.dist(self.pos)
        if not chicken.eggs:
            dist += 100 # The closest eggs have to be *far* away to be safe
        return dist

    def _catch_chicken(self, chicken):
        """The Rinkhals eats eggs, but does not harm chickens"""
        chicken.remove_eggs()
        self.closest = None
        self.hunting = False
        self.target = self.start_pos
        self._last_steps = []

    def _dig(self, dig_pos):
        """Snakes ignore fences"""
        return dig_pos

    def damage(self):
        """The Rinkhals is invincible!"""
        return True

def _get_vision_param(parameter, watcher):
    param = getattr(watcher, parameter)
    for e in watcher.surveillance_equipment():
        modifier = getattr(e, 'MODIFY_'+parameter, lambda r: r)
        param = modifier(param)
    if watcher.abode:
        modifier = getattr(watcher.abode.building, 'MODIFY_'+parameter, lambda r: r)
        param = modifier(param)
    return param

def visible(watcher, watchee, gameboard):
    if not gameboard.in_bounds(watchee.pos):
        # We can't see anything off the edge of the board.
        return False
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
    woods = len([pos for pos in positions if gameboard.is_woodland_tile(pos)])
    roll = random.randint(1, 100)
    return roll > watchee.STEALTH - vision_bonus + range_penalty*distance + constants.WOODLAND_CONCEALMENT*woods

# These don't have to add up to 100, but it's easier to think
# about them if they do.
DEFAULT_FOX_WEIGHTINGS = (
    (Fox, 44),
    (GreedyFox, 20),
    (ShieldFox, 10),
    (RobberFox, 10),
    (NinjaFox, 10),
    (DemoFox, 5),
    (Rinkhals, 1),
    )

