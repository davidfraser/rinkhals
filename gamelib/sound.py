import os
import pygame

import data
import constants

SOUND_INITIALIZED = False

def init_sound():
    """initialize the sound system"""
    global SOUND_INITIALIZED
    try:
        pygame.mixer.init(constants.FREQ, constants.BITSIZE, constants.CHANNELS, constants.BUFFER)
        SOUND_INITIALIZED = True
    except pygame.error, exc:
        print >>sys.stderr, "Could not initialize sound system: %s" % exc

SOUND_CACHE = {}

def play_sound(filename):
    """plays the sound with the given filename from the data sounds directory"""
    if not SOUND_INITIALIZED:
        return
    file_path = data.filepath("sounds", filename)
    sound = SOUND_CACHE.get(file_path, None)
    if not sound:
        if not os.path.exists(file_path):
            return
        SOUND_CACHE[file_path] = sound = pygame.mixer.Sound(file_path)
    sound.play()


