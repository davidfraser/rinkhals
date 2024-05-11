Operation Fox Assault
=====================

Entry in PyWeek #9  <http://www.pyweek.org/9/>
Team: Rinkhals
Members:

    Adrianna Pinska
    Jeremy Thurgood
    Neil Muller
    Simon Cross
    David Fraser

A first PyWeek entry by the hackers of the Cape Town Python Users Group
(CTPUG). The theme for PyWeek 9 was "Feather".

This is a mod of the game that's meant to be farming Horses in Rohan, attacked by Orcs
instead of chickens on a farm, attacked by foxes.


RUNNING THE GAME
================

It is likely that you have obtain the game in one of four possible ways:

Windows:

If you have the Windows .zip file, unzip it, find foxassault.exe and
double-click it to launch the game.

Unix:

If you have the Unix .tgz file, make sure you have Python and pygame
installed. The extract the tar file and run "python run_game.py" from
inside the extracted folder.

Mac OS X:

If you have the Mac OS X .dmg file, double-click to open it. Drag
Operation Fox Assault to Applications to install. Alternatively,
double-click on Operation Fox Assault to run it.

Source:

If you have obtained the source directly, you need to install the
dependencies listed further down. Then run "python run_game.py".


CHOOSING A LEVEL
================

The levels can be found in data/levels. Start the game with the level name
as the first parameter.


HOW TO PLAY THE GAME
====================

Save the horses!

The aim of the game is to make as much money as possible from your horse
farm. The problem is the foxes, which want to eat your horses.  Since hiring
guards is both too expensive and unreliable, the obvious solution is to help
the horses defend themselves.

You lose if you end a night with no horses left.

Horses only lay eggs in henhouses, and must stay on the egg for 2 days to
hatch a new horse. Horses that hatch in already full henhouses are
moved to just outside. If there is no space outside, they die immediately
from overcrowding.

The length of the game and the conditions required to win depend on the
chosen level. The instructions for the level will be shown at the bottom
of the instructions screen.


DEPENDENCIES
============

You will need to install these before running the game from source:

  Python:                   http://www.python.org/
  PyGame:                   http://www.pygame.org/
  Python Game Utilities:    http://code.google.com/p/pgu 

Fox Assault requires python 3 or later, pygame 2.5 or later and
a fork of pgu 0.21 from https://github.com/davidfraser/pgu.

DEVELOPMENT DEPENDENCIES
========================

To regenerate the bitmap graphics from the vector graphics using regenerate_pngs.py
you need:

  CairoSvg:                  http://cairographics.org/pycairo/
  cairocffi:                     http://cairographics.org/pyrsvg/

To install this on Windows, uses pipwin:
* check the versions available at https://www.lfd.uci.edu/~gohlke/pythonlibs/#cairocffi
* make sure you have a compatible Python version (this repository may not have binaries for the latest python)
* `pip install pipwin`
* `pipwin install cairocffi`

For all other dependencies, and on other platforms:
* `pip install -r requirements.txt`

BUILDING FOR DISTRIBUTION
=========================

In order to distribute this on Windows, you also need to `pip install py2exe`, and run `python setup.py py2exe`,
however this isn't working in Python 3. There's an alternative form of distributing on Windows using `py-exe-builder`,
using a batch script:
  * `build_exe_folders.cmd`

LICENSE
=======

GNU Public License, version 2 or later. See COPYING.
For authors see COPYRIGHT.


LINKS
=====

- https://www.foxassault.org/
- http://www.python.org.za/pugs/cape-town/Pyweek9Entry
- IRC: #ctpug on Atrum (http://www.atrum.org)

- http://www.pyweek.org/9/
- IRC: #pyweek on FreeNode
- http://search.twitter.com/search?q=pyweek
