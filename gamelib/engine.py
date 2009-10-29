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
        self.level = level.Level(level_name)
        self.clock = pygame.time.Clock()
        self.main_menu = mainmenu.make_main_menu(self.level)
        self._open_window = None
        self.scoreboard = gameover.ScoreTable(self.level)
        self.gameboard = None

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
        self.gameboard = gameboard.GameBoard(self.main_app,
                self.level)
        self.open_window(self.gameboard.get_top_widget())

    def set_main_menu(self):
        """Open the main menu"""
        self.open_window(self.main_menu)

    def set_help_screen(self):
        """Open the main menu"""
        help_screen = helpscreen.make_help_screen()
        self.open_window(help_screen)

    def create_game_over(self):
        """Create and open the Game Over window"""
        game_over = gameover.create_game_over(self.gameboard,
                self.scoreboard[self.level.level_name], self.level)
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
        pygame.time.set_timer(ANIM_ID, SLOW_ANIM_SPEED)
        self.game.gameboard.advance_day()
        self.game.gameboard.clear_foxes()
        sound.background_music("daytime.ogg")
        self.game.gameboard.hatch_eggs()
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
        elif e.type is ANIM_ID:
            self.game.gameboard.run_animations()
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
        self.game.gameboard.start_night()

        sound.play_sound("nightfall.ogg")
        # Add a timer to the event queue
        self.cycle_count = 0
        self.cycle_time = SLOW_ANIM_SPEED
        pygame.time.set_timer(MOVE_FOX_ID, 4*self.cycle_time)
        pygame.time.set_timer(ANIM_ID, self.cycle_time)
        self.game.gameboard.spawn_foxes()
        sound.background_music("nighttime.ogg")

        self.game.gameboard.lay_eggs()
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
            if self.game.gameboard.is_game_over():
                return GameOver(self.game)
            return DayState(self.game)
        elif (e.type is KEYDOWN and e.key == K_d) or \
                events_equal(e, FAST_FORWARD):
            if self.cycle_time > FAST_ANIM_SPEED:
                self.cycle_time = FAST_ANIM_SPEED
            else:
                self.cycle_time = SLOW_ANIM_SPEED
            pygame.time.set_timer(ANIM_ID, self.cycle_time)
            pygame.time.set_timer(MOVE_FOX_ID, 4*self.cycle_time)
        elif e.type is KEYDOWN and e.key == K_ESCAPE:
            self.dialog = check_exit()
        elif e.type is ANIM_ID:
            self.game.gameboard.run_animations()
        elif e.type is MOVE_FOX_ID:
            # ensure no timers trigger while we're running
            pygame.time.set_timer(ANIM_ID, 0)
            pygame.time.set_timer(MOVE_FOX_ID, 0)
            # Clear any queued timer events, so we don't full the queue
            pygame.event.clear(ANIM_ID)
            pygame.event.clear(MOVE_FOX_ID)
            # Ensure any outstanding animitions get cleaned up
            self.game.gameboard.run_animations()
            self.cycle_count += 1
            if self.cycle_count > constants.NIGHT_LENGTH:
                return pygame.event.post(START_DAY)
            if self.game.gameboard.move_foxes():
                # All foxes are gone/safe, so dawn happens
                return pygame.event.post(START_DAY)
            # Re-enable timers
            pygame.time.set_timer(ANIM_ID, self.cycle_time)
            pygame.time.set_timer(MOVE_FOX_ID, 4*self.cycle_time)
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
        pygame.time.set_timer(ANIM_ID, 0)

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
ANIM_ID = USEREVENT + 6
MOVE_FOXES = pygame.event.Event(MOVE_FOX_ID, name="MOVE_FOXES")
QUIT = pygame.event.Event(QUIT)

# Due to the way pgu's loop timing works, these will only get proceesed
# at intervals of 10ms, so there's no point in them not being multiples of 10
FAST_ANIM_SPEED=20
SLOW_ANIM_SPEED=50
