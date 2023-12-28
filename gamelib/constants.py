"""Operation Fox Assault constants."""

from pygame.locals import USEREVENT, QUIT
import pygame

# Project metadata

NAME = "Operation Fox Assault"

AUTHORS = [
    ("Adrianna Pinska", "adrianna.pinska@gmail.com", "Confluence"),
    ("Jeremy Thurgood", "firxen+rinkhals@gmail.com", "Jerith"),
    ("Neil Muller", "drnlmuller+rinkhals@gmail.com", "Nitwit"),
    ("Simon Cross", "hodgestar+rinkhals@gmail.com", "Hodgestar"),
    ("David Fraser", "davidroyfraser+rinkhals@gmail.com", "Davidf"),
]

# GUI constants

SCREEN = (1850, 1020)
FG_COLOR = (255, 255, 255)
PREDATOR_COUNT_COLOR = (255, 100, 0) # Approximately fox coloured
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
DEFAULT_SELL_PRICE_CHICKEN = 10
DEFAULT_SELL_PRICE_EGG = 5
DEFAULT_SELL_PRICE_DEAD_FOX = 15
DEFAULT_TURN_LIMIT = 14
DEFAULT_GOAL_DESC = 'Survive for 2 weeks'

DEFAULT_MAX_FOXES = 50

# Game constants, still to be made configurable

LOGGING_PRICE = 50
WOODLAND_CONCEALMENT = 10

# Toolbar constants

TOOL_SELECT_CHICKENS = 1
TOOL_SELL_CHICKEN = 2
TOOL_SELL_EGG = 3
TOOL_SELL_BUILDING = 4
TOOL_REPAIR_BUILDING = 5
TOOL_PLACE_ANIMALS = 6
TOOL_LOGGING = 7

NIGHT_LENGTH = 150

TILE_DIMENSIONS = (33, 33)
TOOLBAR_WIDTH = 140


# Game states
START_DAY = pygame.event.Event(USEREVENT, name="START_DAY")
START_NIGHT = pygame.event.Event(USEREVENT, name="START_NIGHT")
GO_MAIN_MENU = pygame.event.Event(USEREVENT, name="GO_MAIN_MENU")
GO_HELP_SCREEN = pygame.event.Event(USEREVENT, name="GO_HELP_SCREEN")
GO_GAME_OVER = pygame.event.Event(USEREVENT, name="GO_GAME_OVER")
FAST_FORWARD = pygame.event.Event(USEREVENT, name="FAST_FORWARD")
MOVE_FOX_ID = USEREVENT + 11
MOVE_FOXES = pygame.event.Event(MOVE_FOX_ID, name="MOVE_FOXES")
DO_LOAD_SAVEGAME = USEREVENT + 12
DO_LOAD_LEVEL = USEREVENT + 13
DO_QUIT = pygame.event.Event(QUIT)
