"""Game engine and states."""
from pgu.engine import Game, State, Quit
import pygame
from pygame.locals import USEREVENT, QUIT, KEYDOWN, K_ESCAPE, K_n, K_d, K_s, K_i

import gameboard
import gameover
import sound
import constants
import mainmenu
import helpscreen
import level
from misc import check_exit

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
        self.scoreboard = gameover.ScoreTable(self.level)
        main_menu = mainmenu.make_main_menu(self.level)
        self.open_window(main_menu)

    def set_help_screen(self):
        """Open the main menu"""
        help_screen = helpscreen.make_help_screen(self.level)
        self.open_window(help_screen)

    def create_game_over(self):
        """Create and open the Game Over window"""
        level = self.gameboard.level
        game_over = gameover.create_game_over(self.gameboard,
                self.scoreboard[level.level_name], level)
        self.gameboard = None
        self.open_window(game_over)

    def event(self, e):
        if not Game.event(self, e):
            if self.gameboard:
                return self.gameboard.event(e)
            return False
        return True


class MainMenuState(State):
    def init(self):
        sound.stop_background_music()
        self.game.set_main_menu()

    def event(self, e):
        if events_equal(e, START_DAY):
            self.game.create_game_board()
            return DayState(self.game)
        elif events_equal(e, GO_HELP_SCREEN):
            return HelpScreenState(self.game)
        elif e.type is KEYDOWN:
            if e.key == K_ESCAPE:
                return Quit(self.game)
            elif e.key == K_s:
                self.game.create_game_board()
                return DayState(self.game)
            elif e.key == K_i:
                return HelpScreenState(self.game)
        elif e.type is DO_LOAD_LEVEL:
            self.game.load_new_level(e.level)
            return
        elif e.type is DO_LOAD_SAVEGAME:
            self.game.switch_gameboard(e.gameboard)
            e.gameboard.skip_next_start_day()
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

class HelpScreenState(State):
    def init(self):
        sound.stop_background_music()
        self.game.set_help_screen()

    def event(self, e):
        if e.type is KEYDOWN and e.key == K_ESCAPE:
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


class DayState(State):
    def init(self):
        """Add some chickens to the farm"""
        sound.stop_background_music()
        self.game.gameboard.start_day()

        sound.play_sound("daybreak.ogg")
        # disable timer
        pygame.time.set_timer(MOVE_FOX_ID, 0)
        sound.background_music("daytime.ogg")
        self.dialog = None

    def event(self, e):
        if self.dialog and self.dialog.running:
            if self.dialog.event(e):
                return
        elif self.dialog:
            if self.dialog.do_quit:
                self.dialog = None
                self.game.gameboard.reset_states()
                return GameOver(self.game)
            self.dialog=None
            return
        if events_equal(e, START_NIGHT):
            self.game.gameboard.reset_states()
            return NightState(self.game)
        elif e.type is KEYDOWN and e.key == K_ESCAPE:
            self.dialog = check_exit()
        elif e.type is KEYDOWN and e.key == K_n:
            return pygame.event.post(START_NIGHT)
        elif events_equal(e, GO_MAIN_MENU):
            return MainMenuState(self.game)
        elif e.type is DO_LOAD_SAVEGAME:
            self.game.switch_gameboard(e.gameboard)
            return
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
        self.game.gameboard.start_night()

        sound.play_sound("nightfall.ogg")

        self.game.gameboard.chickens_scatter()
        self.game.gameboard.chickens_chop_wood()
        # Add a timer to the event queue
        self.cycle_count = 0
        self.cycle_time = SLOW__SPEED
        pygame.time.set_timer(MOVE_FOX_ID, self.cycle_time)
        sound.background_music("nighttime.ogg")

        self.dialog = None

    def event(self, e):
        if self.dialog and self.dialog.running:
            if self.dialog.event(e):
                return
        elif self.dialog:
            if self.dialog.do_quit:
                self.dialog = None
                self.game.gameboard.reset_states()
                return GameOver(self.game)
            self.dialog=None
            return
        if events_equal(e, START_DAY):
            if self.game.gameboard.level.is_game_over(self.game.gameboard):
                return GameOver(self.game)
            return DayState(self.game)
        elif (e.type is KEYDOWN and e.key == K_d) or \
                events_equal(e, FAST_FORWARD):
            if self.cycle_time > FAST__SPEED:
                self.cycle_time = FAST__SPEED
            else:
                self.cycle_time = SLOW__SPEED
            pygame.time.set_timer(MOVE_FOX_ID, self.cycle_time)
        elif e.type is KEYDOWN and e.key == K_ESCAPE:
            self.dialog = check_exit()
        elif e.type is MOVE_FOX_ID:
            # ensure no timers trigger while we're running
            pygame.time.set_timer(MOVE_FOX_ID, 0)
            cur_time = pygame.time.get_ticks()
            # Clear any queued timer events, so we don't full the queue
            pygame.event.clear(MOVE_FOX_ID)
            # Ensure any outstanding animitions get cleaned up
            self.cycle_count += 1
            if self.cycle_count > constants.NIGHT_LENGTH:
                return pygame.event.post(START_DAY)
            if self.game.gameboard.do_night_step():
                # All foxes are gone/safe, so dawn happens
                return pygame.event.post(START_DAY)
            # Re-enable timers
            diff = pygame.time.get_ticks() - cur_time
            time_left = self.cycle_time - diff
            if time_left <= 0:
                time_left = self.cycle_time
            pygame.time.set_timer(MOVE_FOX_ID, time_left)
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
        sound.stop_background_music()
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
GO_HELP_SCREEN = pygame.event.Event(USEREVENT, name="GO_HELP_SCREEN")
FAST_FORWARD = pygame.event.Event(USEREVENT, name="FAST_FORWARD")
MOVE_FOX_ID = USEREVENT + 1
MOVE_FOXES = pygame.event.Event(MOVE_FOX_ID, name="MOVE_FOXES")
DO_LOAD_SAVEGAME = USEREVENT + 2
DO_LOAD_LEVEL = USEREVENT + 3
QUIT = pygame.event.Event(QUIT)

# Due to the way pgu's loop timing works, these will only get proceesed
# at intervals of 10ms, so there's no point in them not being multiples of 10
FAST__SPEED=80
SLOW__SPEED=200
