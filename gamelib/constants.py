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
BG_COLOR = (0, 0, 0)

# Mixer constants
FREQ = 44100   # same as audio CD
BITSIZE = -16  # unsigned 16 bit
CHANNELS = 2   # 1 == mono, 2 == stereo
BUFFER = 1024  # audio buffer size in no. of samples
FRAMERATE = 30 # how often to check if playback has finished

# Game constants

STARTING_CASH = 1000
SELL_PRICE_CHICKEN = 10
SELL_PRICE_EGG = 5
SELL_PRICE_DEAD_FOX = 15
LOGGING_PRICE = 50
BUY_PRICE_FENCE = 50
SELL_PRICE_FENCE = 25
REPAIR_PRICE_FENCE = 25
SELL_PRICE_BROKEN_FENCE = 5

TOOL_SELL_CHICKEN = 1
TOOL_SELL_EGG = 2
TOOL_SELL_BUILDING = 3
TOOL_BUY_FENCE = 4
TOOL_PLACE_ANIMALS = 5
TOOL_LOGGING = 6
TOOL_SELL_EQUIPMENT = 7

NIGHT_LENGTH = 150

TURN_LIMITS = {
        'Two weeks' : 14,
        'Three months' : 90,
        'Unlimited' : 0,
        }

# This is a "constant".
TURN_LIMIT = TURN_LIMITS['Two weeks']

ABS_MAX_NUM_FOXES = 50 # Limit possible uppoer number of foxes, due to concerns
                        # about performance, etc.

START_CHICKENS = 10
