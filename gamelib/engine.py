"""Game engine and states."""
from pgu.engine import Game, State
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE

from . import gameboard
from . import gameover
from . import sound
from . import constants
from . import mainmenu
from . import helpscreen
from . import level

class Engine(Game):
    def __init__(self, main_app, level_name):
        self.main_app = main_app
        self.clock = pygame.time.Clock()
        self.level = level.Level(level_name)
        self._open_window = None
        self.gameboard = None

    def tick(self):
        """Tic toc."""
        pygame.time.wait(10)

    def load_new_level(self, new_level):
        self.level = new_level

    def open_window(self, window):
        """Open a widget as the main window."""
        if self._open_window is not None:
            self.main_app.close(self._open_window)
        self.main_app.open(window)
        self._open_window = window

    def create_game_board(self):
        """Create and open a gameboard window."""
        self.gameboard = gameboard.GameBoard(self.main_app,
                self.level)
        self.open_window(self.gameboard.get_top_widget())

    def switch_gameboard(self, new_gameboard):
        """Switch over to a new gameboard."""
        self.gameboard = new_gameboard
        self.gameboard.disp = self.main_app
        self.gameboard.create_display()
        self.open_window(self.gameboard.get_top_widget())

    def set_main_menu(self):
        """Open the main menu"""
        main_menu = mainmenu.make_main_menu(self.level)
        self.open_window(main_menu)

    def set_help_screen(self):
        """Open the main menu"""
        help_screen = helpscreen.make_help_screen(self.level)
        self.open_window(help_screen)

    def create_game_over(self):
        """Create and open the Game Over window"""
        level = self.gameboard.level
        game_over = gameover.create_game_over(self.gameboard, level)
        self.gameboard = None
        self.open_window(game_over)

    def event(self, e):
        return Game.event(self, e)


class MainMenuState(State):
    def init(self):
        sound.stop_background_music()
        self.game.set_main_menu()

    def event(self, e):
        if events_equal(e, constants.START_DAY):
            self.game.create_game_board()
            return DayState(self.game)
        elif events_equal(e, constants.GO_HELP_SCREEN):
            return HelpScreenState(self.game)
        elif e.type == constants.DO_LOAD_LEVEL:
            self.game.load_new_level(e.level)
            return
        elif e.type == constants.DO_LOAD_SAVEGAME:
            self.game.switch_gameboard(e.gameboard)
            e.gameboard.skip_next_start_day()
            return DayState(self.game)

        self.game.main_app.event(e)

    def paint(self, screen):
        screen.fill((0,0,0))
        self.game.main_app.paint(screen)
        pygame.display.flip()

    def update(self, screen):
        update = self.game.main_app.update(screen)
        pygame.display.update(update)

class HelpScreenState(State):
    def init(self):
        sound.stop_background_music()
        self.game.set_help_screen()

    def event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            return MainMenuState(self.game)
        elif events_equal(e, constants.GO_MAIN_MENU):
            return MainMenuState(self.game)
        elif e.type != constants.DO_QUIT:
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
        self.game.gameboard.start_day()

        sound.play_sound("daybreak.ogg")
        # disable timer
        pygame.time.set_timer(constants.MOVE_FOX_ID, 0)
        sound.background_music("daytime.ogg")

    def event(self, e):
        if events_equal(e, constants.START_NIGHT):
            self.game.gameboard.reset_states()
            return NightState(self.game)
        elif events_equal(e, constants.GO_GAME_OVER):
            return GameOver(self.game)
        elif events_equal(e, constants.GO_MAIN_MENU):
            return MainMenuState(self.game)
        elif e.type == constants.DO_LOAD_SAVEGAME:
            self.game.switch_gameboard(e.gameboard)
            return

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
        self.game.gameboard.start_night()

        sound.play_sound("nightfall.ogg")

        # Add a timer to the event queue
        self.cycle_count = 0
        self.cycle_time = SLOW__SPEED
        pygame.time.set_timer(constants.MOVE_FOX_ID, self.cycle_time)
        sound.background_music("nighttime.ogg")

        self.dialog = None

    def event(self, e):
        if events_equal(e, constants.START_DAY):
            if self.game.gameboard.level.is_game_over(self.game.gameboard):
                return GameOver(self.game)
            return DayState(self.game)
        elif events_equal(e, constants.GO_GAME_OVER):
            return GameOver(self.game)
        elif events_equal(e, constants.FAST_FORWARD):
            if self.cycle_time > FAST__SPEED:
                self.cycle_time = FAST__SPEED
            else:
                self.cycle_time = SLOW__SPEED
            pygame.time.set_timer(constants.MOVE_FOX_ID, self.cycle_time)
            return
        elif e.type == constants.MOVE_FOX_ID:
            # ensure no timers trigger while we're running
            pygame.time.set_timer(constants.MOVE_FOX_ID, 0)
            cur_time = pygame.time.get_ticks()
            # Clear any queued timer events, so we don't fill the queue
            pygame.event.clear(constants.MOVE_FOX_ID)
            # Ensure any outstanding animitions get cleaned up
            self.cycle_count += 1
            if self.cycle_count > constants.NIGHT_LENGTH:
                pygame.event.post(constants.START_DAY)
                return
            if self.game.gameboard.do_night_step():
                # All foxes are gone/safe, so dawn happens
                pygame.event.post(constants.START_DAY)
                return
            # Re-enable timers
            diff = pygame.time.get_ticks() - cur_time
            time_left = self.cycle_time - diff
            if time_left <= 0:
                time_left = self.cycle_time
            pygame.time.set_timer(constants.MOVE_FOX_ID, time_left)
            return

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
        sound.stop_background_music()
        self.game.create_game_over()
        pygame.time.set_timer(constants.MOVE_FOX_ID, 0)

    def event(self, e):
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                return MainMenuState(self.game)
        elif events_equal(e, constants.GO_MAIN_MENU):
            return MainMenuState(self.game)
        elif e.type != constants.DO_QUIT:
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
    return (e1.type == e2.type and e1.name == e2.name)

# Due to the way pgu's loop timing works, these will only get proceesed
# at intervals of 10ms, so there's no point in them not being multiples of 10
FAST__SPEED=80
SLOW__SPEED=200
