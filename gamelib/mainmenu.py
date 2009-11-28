"""Main menu."""

from pgu import gui
import pygame
import constants
import engine
import imagecache
import gameboard
import gameover
import savegame
import loadlevel

def make_main_menu(level):
    """Create a main menu"""
    main_menu = MainMenu(level)

    c = MenuContainer(align=0, valign=0)
    c.add(main_menu, 0, 0)

    return c

class MenuContainer(gui.Container):
    def paint(self, s):
        pygame.display.set_caption(constants.NAME)
        splash = imagecache.load_image("images/splash.png")
        pygame.display.get_surface().blit(splash, (0, 0))
        gui.Container.paint(self, s)

    def get_mode(self):
        return self.widgets[0].mode

class MainMenu(gui.Table):
    def __init__(self, level, **params):
        gui.Table.__init__(self, **params)
        self.mode = None
        self.level = level

        def fullscreen_toggled():
            pygame.display.toggle_fullscreen()

        def quit_pressed():
            pygame.event.post(engine.QUIT)

        def start_game():
            pygame.event.post(engine.START_DAY)

        def choose_level():
            def load_func(new_level):
                pygame.event.post(pygame.event.Event(engine.DO_LOAD_LEVEL, level=new_level))
                self.level = new_level
                self.redraw()
            loadlevel.LoadLevelDialog(level, load_func).open()

        def load_game():
            savegame.RestoreDialog(gameboard.GameBoard.restore_game).open()

        def scores_pressed():
            scoreboard = gameover.Scoreboard(self.level)
            title = gui.Label("High Scores for Level %s" % self.level.level_name)
            gui.Dialog(title, scoreboard).open()

        def help_pressed():
            pygame.event.post(engine.GO_HELP_SCREEN)

        style = {
            "padding_bottom": 15,
        }
        td_kwargs = {
            "align": 0,
            "style": style,
        }

        change_button = gui.Button('Choose level')
        change_button.connect(gui.CLICK, choose_level)
        self.tr()
        self.td(change_button, **td_kwargs)

        self.start_button = gui.Button(level.level_name)
        self.start_button.connect(gui.CLICK, start_game)
        self.tr()
        self.td(self.start_button, **td_kwargs)

        loadgame_button = gui.Button('Restore Game')
        loadgame_button.connect(gui.CLICK, load_game)
        self.tr()
        self.td(loadgame_button, **td_kwargs)

        help_button = gui.Button("Instructions")
        help_button.connect(gui.CLICK, help_pressed)
        self.tr()
        self.td(help_button, **td_kwargs)

        scores_button = gui.Button("High Scores")
        scores_button.connect(gui.CLICK, scores_pressed)
        self.tr()
        self.td(scores_button, **td_kwargs)

        quit_button = gui.Button("Quit")
        quit_button.connect(gui.CLICK, quit_pressed)
        self.tr()
        self.td(quit_button, **td_kwargs)

        # fullscreen_toggle = gui.Button("Toggle Fullscreen")
        # fullscreen_toggle.connect(gui.CLICK, fullscreen_toggled)
        # self.tr()
        # self.td(fullscreen_toggle, **td_kwargs)


    def redraw(self):
        self.start_button.value = self.level.level_name
