'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import pygame
from pgu import gui
from pygame.locals import SWSURFACE, QUIT, KEYDOWN, K_ESCAPE

from mainmenu import MainMenu
import constants

def gameloop(screen, app):
    """Main game loop."""
    clock = pygame.time.Clock()
    done = False
    while not done:
        for e in pygame.event.get():
            if e.type is QUIT:
                done = True
            elif e.type is KEYDOWN and e.key == K_ESCAPE:
                done = True
            else:
                app.event(e)

        # Clear the screen and render the stars
        dt = clock.tick()/1000.0
        screen.fill((0,0,0))
        app.paint(screen)
        pygame.display.flip()
        pygame.time.wait(10)


def main():
    """Main script."""
    screen = pygame.display.set_mode(constants.SCREEN, SWSURFACE)

    form = gui.Form()
    app = gui.App()
    main_menu = MainMenu()

    c = gui.Container(align=-1, valign=-1)
    c.add(main_menu, 0, 0)

    app.init(c)

    gameloop(screen, app)
