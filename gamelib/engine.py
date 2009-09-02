"""Game engine and states."""

from pgu.engine import Game, State, Quit
import pygame
from pygame.locals import USEREVENT, QUIT, KEYDOWN, K_ESCAPE, K_n, K_d, K_s

import gameboard
import sound

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

        sound.play_sound("daybreak.ogg")
        # disable timer
        pygame.time.set_timer(MOVE_FOX_ID, 0)
        self.game.gameboard.clear_foxes()
        self.game.gameboard.update_chickens()

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

        sound.play_sound("nightfall.ogg")
        # Add a timer to the event queue
        self.cycle_count = 0
        pygame.time.set_timer(MOVE_FOX_ID, 200)
        self.game.gameboard.spawn_foxes()

    def event(self, e):
        if events_equal(e, START_DAY):
            return DayState(self.game)
        elif e.type is KEYDOWN and e.key == K_d:
            return pygame.event.post(START_DAY)
        elif e.type is KEYDOWN and e.key == K_ESCAPE:
            return MainMenuState(self.game)
        elif e.type is MOVE_FOX_ID:
            self.cycle_count += 1
            if self.cycle_count > NIGHT_LENGTH:
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
NIGHT_LENGTH = 150
