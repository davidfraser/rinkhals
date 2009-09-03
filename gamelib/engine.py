"""Game engine and states."""

from pgu.engine import Game, State, Quit
import pygame
from pygame.locals import USEREVENT, QUIT, KEYDOWN, K_ESCAPE, K_n, K_d, K_s

import gameboard
import gameover
import sound
import constants
import mainmenu

class Engine(Game):
    def __init__(self, main_app):
        self.main_app = main_app
        self.clock = pygame.time.Clock()
        self.main_menu = mainmenu.make_main_menu()
        self._open_window = None

    def tick(self):
        """Tic toc."""
        pygame.time.wait(10)

    def open_window(self, window):
        """Open a widget as the main window."""
        if self._open_window is not None:
            self.main_app.close(self._open_window)
        self.main_app.open(window)
        self._open_window = window

    def create_game_board(self):
        """Create and open a gameboard window."""
        self.gameboard = gameboard.GameBoard(self.main_app)
        self.open_window(self.gameboard.get_top_widget())

    def set_main_menu(self):
        """Open the main menu"""
        self.open_window(self.main_menu)

    def create_game_over(self):
        """Create and open the Game Over window"""
        game_over = gameover.create_game_over(self.gameboard)
        self.open_window(game_over)

class MainMenuState(State):
    def init(self):
        self.game.set_main_menu()

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
            self.game.main_app.event(e)

    def paint(self, screen):
        screen.fill((0,0,0))
        self.game.main_app.paint(screen)
        pygame.display.flip()

    def update(self, screen):
        update = self.game.main_app.update(screen)
        pygame.display.update(update)

class DayState(State):
    def init(self):
        """Add some chickens to the farm"""
        sound.stop_background_music()
        self.game.gameboard.tv.sun(True)

        sound.play_sound("daybreak.ogg")
        # disable timer
        pygame.time.set_timer(MOVE_FOX_ID, 0)
        self.game.gameboard.advance_day()
        self.game.gameboard.clear_foxes()
        sound.background_music("daytime.ogg")
        self.game.gameboard.hatch_eggs()

    def event(self, e):
        if events_equal(e, START_NIGHT):
            return NightState(self.game)
        elif e.type is KEYDOWN and e.key == K_ESCAPE:
            return GameOver(self.game)
        elif e.type is KEYDOWN and e.key == K_n:
            return pygame.event.post(START_NIGHT)
        elif events_equal(e, GO_MAIN_MENU):
            return MainMenuState(self.game)
        elif e.type is not QUIT:
            self.game.main_app.event(e)

    def paint(self, screen):
        self.game.main_app.paint(screen)
        pygame.display.flip()

    def update(self, screen):
        self.game.gameboard.update()
        update = self.game.main_app.update(screen)
        pygame.display.update(update)

    def loop(self):
        self.game.gameboard.loop()

class NightState(State):
    def init(self):
        """Add some foxes to the farm"""
        sound.stop_background_music()
        self.game.gameboard.tv.sun(False)

        sound.play_sound("nightfall.ogg")
        # Add a timer to the event queue
        self.cycle_count = 0
        pygame.time.set_timer(MOVE_FOX_ID, 200)
        self.game.gameboard.spawn_foxes()
        sound.background_music("nighttime.ogg")

        self.game.gameboard.lay_eggs()

    def event(self, e):
        if events_equal(e, START_DAY):
            if self.game.gameboard.is_game_over():
                return GameOver(self.game)
            return DayState(self.game)
        elif e.type is KEYDOWN and e.key == K_d:
            return pygame.event.post(START_DAY)
        elif e.type is KEYDOWN and e.key == K_ESCAPE:
            return GameOver(self.game)
        elif e.type is MOVE_FOX_ID:
            self.cycle_count += 1
            if self.cycle_count > constants.NIGHT_LENGTH:
                return pygame.event.post(START_DAY)
            if self.game.gameboard.move_foxes():
                # All foxes are gone/safe, so dawn happens
                return pygame.event.post(START_DAY)
        elif e.type is not QUIT:
            self.game.main_app.event(e)

    def loop(self):
        self.game.gameboard.loop()

    def paint(self, screen):
        self.game.main_app.paint(screen)
        pygame.display.flip()

    def update(self, screen):
        self.game.gameboard.update()
        update = self.game.main_app.update(screen)
        pygame.display.update(update)

class GameOver(State):
    def init(self):
        """Setup everything"""
        self.game.create_game_over()
        pygame.time.set_timer(MOVE_FOX_ID, 0)

    def event(self, e):
        if e.type is KEYDOWN:
            if e.key == K_ESCAPE:
                return MainMenuState(self.game)
        elif events_equal(e, GO_MAIN_MENU):
            return MainMenuState(self.game)
        elif e.type is not QUIT:
            self.game.main_app.event(e)

    def paint(self, screen):
        screen.fill((0,0,0))
        self.game.main_app.paint(screen)
        pygame.display.flip()

    def update(self, screen):
        update = self.game.main_app.update(screen)
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
