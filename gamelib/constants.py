"""Operation Fox Assault constants."""

# Project metadata

NAME = "Operation Fox Assault"

AUTHORS = [
    ("Adrianna Pinska", "adrianna.pinska@gmail.com"),
    ("Jeremy Thurgood", "firxen+rinkhals@gmail.com"),
    ("Neil Muller", ""),
    ("Simon Cross", "hodgestar+rinkhals@gmail.com"),
]

# GUI constants

SCREEN = (800, 600)
FG_COLOR = (255, 255, 255)
PREDATOR_COUNT_COLOR = (255, 100, 0) # Approximately fox coloured
BG_COLOR = (0, 0, 0)

# Mixer constants
FREQ = 44100   # same as audio CD
BITSIZE = -16  # unsigned 16 bit
CHANNELS = 2   # 1 == mono, 2 == stereo
BUFFER = 1024  # audio buffer size in no. of samples
FRAMERATE = 30 # how often to check if playback has finished

# Default values that can be overridden by the levels

DEFAULT_STARTING_CASH = 1000
DEFAULT_SELL_PRICE_CHICKEN = 10
DEFAULT_SELL_PRICE_EGG = 5
DEFAULT_SELL_PRICE_DEAD_FOX = 15
DEFAULT_TURN_LIMIT = 14
DEFAULT_GOAL_DESC = 'Survive for 2 weeks'

DEFAULT_MAX_FOXES = 50

# Game constants, still to be made configurable

LOGGING_PRICE = 50

# Toolbar constants

TOOL_SELL_CHICKEN = 1
TOOL_SELL_EGG = 2
TOOL_SELL_BUILDING = 3
TOOL_REPAIR_BUILDING = 4
TOOL_PLACE_ANIMALS = 5
TOOL_LOGGING = 6
TOOL_SELL_EQUIPMENT = 7

NIGHT_LENGTH = 150


