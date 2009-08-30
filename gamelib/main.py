'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

SCREEN = (800, 600)

import time
import random

import pygame
from pgu import gui
from pygame.locals import *

from mainmenu import MainMenu

W,H = 640,480
W2,H2 = 320,240

##Using App instead of Desktop removes the GUI background.  Note the call to app.init()
##::

form = gui.Form()

app = gui.App()
main_menu = MainMenu()

c = gui.Container(align=-1,valign=-1)
c.add(main_menu,0,0)

app.init(c)
##

dist = 8192
span = 10
stars = []
def reset():
    global stars
    stars = []
    for i in range(0,form['quantity'].value):
        stars.append([random.randrange(-W*span,W*span),
                      random.randrange(-H*span,H*span),
                      random.randrange(1,dist)])
        

def render(dt):
    speed = form['speed'].value*10
    size = form['size'].value
    color = form['color'].value
    warp = form['warp'].value

    colors = []
    for i in range(256,0,-1):
        colors.append((color[0]*i/256,color[1]*i/256,color[2]*i/256))
        
    n = 0
    for x,y,z in stars:
        if warp:
            z1 = max(1,z + speed*2)
            x1 = x*256/z1
            y1 = y*256/z1
            xx1,yy1 = x1+W2,y1+H2
    
        x = x*256/z
        y = y*256/z
        xx,yy = x+W2,y+H2
        c = min(255,z * 255 / dist)
        col = colors[int(c)]

        if warp:
            pygame.draw.line(screen,col,
                             (int(xx1),int(yy1)),
                             (int(xx),int(yy)),size)
        
        pygame.draw.circle(screen,col,(int(xx),int(yy)),size)
        
        ch = 0
        z -= speed*dt
        if z <= 0: 
            ch = 1
            z += dist
        if z > dist: 
            ch = 1
            z -= dist
        if ch:
            stars[n][0] = random.randrange(-W*span,W*span)
            stars[n][1] = random.randrange(-H*span,H*span)
        stars[n][2] = z
        
        n += 1
        
screen = pygame.display.set_mode(SCREEN,SWSURFACE)

##You can include your own run loop.
##::

def gameloop(screen):
    reset()
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
        render(dt)
        app.paint(screen)
        pygame.display.flip()
        pygame.time.wait(10)


def main():
    gameloop(screen)
