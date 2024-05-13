"""Operation Orc Assault constants."""

from pygame.locals import USEREVENT, QUIT
import pygame

# Project metadata

NAME = "Operation Orc Assault"

AUTHORS = [
    ("Adrianna Pinska", "adrianna.pinska@gmail.com", "Confluence"),
    ("Jeremy Thurgood", "firxen+rinkhals@gmail.com", "Jerith"),
    ("Neil Muller", "drnlmuller+rinkhals@gmail.com", "Nitwit"),
    ("Simon Cross", "hodgestar+rinkhals@gmail.com", "Hodgestar"),
    ("David Fraser", "davidroyfraser+rinkhals@gmail.com", "Davidf"),
]

# GUI constants

SCREEN = (1300, 920)
TILE_DIMENSIONS = (28, 28)
TOOLBAR_WIDTH = 180

FG_COLOR = (255, 255, 255)
PREDATOR_COUNT_COLOR = (255, 100, 0) # Approximately orc coloured
SELECTED_COUNT_COLOR = (0, 128, 235) # Selection highlight colour
BG_COLOR = (0, 0, 0)

# Mixer constants
FREQ = 44100   # same as audio CD
BITSIZE = -16  # unsigned 16 bit
CHANNELS = 2   # 1 == mono, 2 == stereo
BUFFER = 1024  # audio buffer size in no. of samples
FRAMERATE = 30 # how often to check if playback has finished

# Default values that can be overridden by the levels

DEFAULT_STARTING_CASH = 1000
DEFAULT_STARTING_WOOD = 50
DEFAULT_SELL_PRICE_HORSE = 10
DEFAULT_SELL_PRICE_EGG = 5
DEFAULT_SELL_PRICE_DEAD_orc = 15
DEFAULT_TURN_LIMIT = 14
DEFAULT_GOAL_DESC = 'Survive for 2 weeks'

DEFAULT_MAX_orcs = 50

# Game constants, still to be made configurable

LOGGING_PRICE = 50
WOODLAND_CONCEALMENT = 10

# Toolbar constants

TOOL_SELECT_HORSES = 1
TOOL_SELL_BUILDING = 4
TOOL_REPAIR_BUILDING = 5
TOOL_PLACE_ANIMALS = 6
TOOL_LOGGING = 7

NIGHT_LENGTH = 150


# Game states
START_DAY = pygame.event.Event(USEREVENT, name="START_DAY")
START_NIGHT = pygame.event.Event(USEREVENT, name="START_NIGHT")
GO_MAIN_MENU = pygame.event.Event(USEREVENT, name="GO_MAIN_MENU")
GO_HELP_SCREEN = pygame.event.Event(USEREVENT, name="GO_HELP_SCREEN")
GO_GAME_OVER = pygame.event.Event(USEREVENT, name="GO_GAME_OVER")
FAST_FORWARD = pygame.event.Event(USEREVENT, name="FAST_FORWARD")
MOVE_orc_ID = USEREVENT + 11
MOVE_orcs = pygame.event.Event(MOVE_orc_ID, name="MOVE_orcs")
DO_LOAD_SAVEGAME = USEREVENT + 12
DO_LOAD_LEVEL = USEREVENT + 13
DO_QUIT = pygame.event.Event(QUIT)
