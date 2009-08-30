"""Game engine and states."""

from pgu.engine import Game, State, Quit
import pygame
from pygame.locals import USEREVENT, QUIT, KEYDOWN, K_ESCAPE, K_n, K_d, K_s

from tiles import TILE_MAP
import gameboard
import animal
import random

class Engine(Game):
    def __init__(self, main_menu_app):
        self.main_menu_app = main_menu_app
        self.clock = pygame.time.Clock()

    def tick(self):
        """Tic toc."""
        pygame.time.wait(10)

    def create_game_board(self):
        self.gameboard = gameboard.GameBoard()

class MainMenuState(State):
    def event(self, e):
        if events_equal(e, START_DAY):
            self.game.create_game_board()
            return DayState(self.game)
        elif e.type is KEYDOWN:
            if e.key == K_ESCAPE:
                return Quit(self.game)
            elif e.key == K_s:
                self.game.create_game_board()
                return DayState(self.game)
        elif e.type is not QUIT:
            self.game.main_menu_app.event(e)

    def paint(self, screen):
        screen.fill((0,0,0))
        self.game.main_menu_app.paint(screen)
        pygame.display.flip()

    def update(self, screen):
        update = self.game.main_menu_app.update(screen)
        pygame.display.update(update)

class DayState(State):
    def init(self):
        """Add some chickens to the farm"""
        self.game.gameboard.tv.sun(True)

        # disable timer
        pygame.time.set_timer(MOVE_FOX_ID, 0)
        # Very simple, we walk around the tilemap, and, for each farm tile,
        # we randomly add a chicken (1 in 10 chance) until we have 5 chickens
        # or we run out of board
        self.game.gameboard.clear_foxes()
        chickens = len(self.game.gameboard.chickens)
        x, y = 0, 0
        width, height = self.game.gameboard.tv.size
        while chickens < 5:
            if x < width:
                tile = self.game.gameboard.tv.get((x, y))
            else:
                y += 1
                if y >= height:
                    break
                x = 0
                continue
            # See if we place a chicken
            if 'grassland' == TILE_MAP[tile]:
                # Farmland
                roll = random.randint(1, 20)
                # We don't place within a tile of the fence, this is to make things
                # easier
                for xx in range(x-1, x+2):
                    if xx >= height or xx < 0:
                        continue
                    for yy in range(y-1, y+2):
                        if yy >= height or yy < 0:
                            continue
                        neighbour = self.game.gameboard.tv.get((xx, yy))
                        if 'fence' == TILE_MAP[neighbour]:
                            # Fence
                            roll = 10
                if roll == 1:
                    # Create a chicken
                    chickens += 1
                    chick = animal.Chicken((x, y))
                    self.game.gameboard.add_chicken(chick)
            x += 1

    def event(self, e):
        if events_equal(e, START_NIGHT):
            return NightState(self.game)
        elif e.type is KEYDOWN and e.key == K_ESCAPE:
            return MainMenuState(self.game)
        elif e.type is KEYDOWN and e.key == K_n:
            return pygame.event.post(START_NIGHT)
        elif events_equal(e, GO_MAIN_MENU):
            return MainMenuState(self.game)
        elif e.type is not QUIT:
            self.game.gameboard.event(e)

    def paint(self, screen):
        self.game.gameboard.paint(screen)
        pygame.display.flip()

    def update(self, screen):
        update = self.game.gameboard.update(screen)
        pygame.display.update(update)

    def loop(self):
        self.game.gameboard.loop()

class NightState(State):
    def init(self):
        """Add some foxes to the farm"""
        self.game.gameboard.tv.sun(False)

        # Add a timer to the event queue
        self.cycle_count = 0
        pygame.time.set_timer(MOVE_FOX_ID, 300)
        # Very simple, we walk around the tilemap, and, for each farm tile,
        # we randomly add a chicken (1 in 10 chance) until we have 5 chickens
        # or we run out of board
        foxes = len(self.game.gameboard.foxes)
        x, y = 0, 0
        width, height = self.game.gameboard.tv.size
        while foxes < 5:
            if x < width:
                tile = self.game.gameboard.tv.get((x, y))
            else:
                y += 1
                if y >= height:
                    break
                x = 0
                continue
            # See if we place a fox
            if TILE_MAP[tile] == 'woodland':
                # Forest
                roll = random.randint(1, 20)
                if roll == 1:
                    # Create a fox
                    foxes += 1
                    fox = animal.Fox((x, y))
                    self.game.gameboard.add_fox(fox)
            x += 5

    def event(self, e):
        if events_equal(e, START_DAY):
            return DayState(self.game)
        elif e.type is KEYDOWN and e.key == K_d:
            return pygame.event.post(START_DAY)
        elif e.type is KEYDOWN and e.key == K_ESCAPE:
            return MainMenuState(self.game)
        elif e.type is MOVE_FOX_ID:
            self.cycle_count += 1
            if self.cycle_count > 15:
                return pygame.event.post(START_DAY)
            return self.game.gameboard.move_foxes()
        elif e.type is not QUIT:
            self.game.gameboard.event(e)

    def loop(self):
        self.game.gameboard.loop()

    def paint(self, screen):
        self.game.gameboard.paint(screen)
        pygame.display.flip()

    def update(self, screen):
        update = self.game.gameboard.update(screen)
        pygame.display.update(update)

# pygame events

def events_equal(e1, e2):
    """Compare two user events."""
    return (e1.type is e2.type and e1.name == e2.name)

START_DAY = pygame.event.Event(USEREVENT, name="START_DAY")
START_NIGHT = pygame.event.Event(USEREVENT, name="START_NIGHT")
GO_MAIN_MENU = pygame.event.Event(USEREVENT, name="GO_MAIN_MENU")
MOVE_FOX_ID = USEREVENT + 1
MOVE_FOXES = pygame.event.Event(MOVE_FOX_ID, name="MOVE_FOXES")
QUIT = pygame.event.Event(QUIT)
