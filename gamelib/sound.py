import os
import sys

import pygame

from . import data
from .config import config
from . import constants

SOUND_INITIALIZED = False

def init_sound():
    """initialize the sound system"""
    global SOUND_INITIALIZED
    if not config.sound:
        return
    try:
        pygame.mixer.init(constants.FREQ, constants.BITSIZE, constants.CHANNELS, constants.BUFFER)
        SOUND_INITIALIZED = True
    except pygame.error as exc:
        print("Could not initialize sound system: %s" % exc, file=sys.stderr)

SOUND_CACHE = {}

def play_sound(filename):
    """plays the sound with the given filename from the data sounds directory"""
    if not (SOUND_INITIALIZED and config.sound):
        return
    file_path = data.filepath("sounds", filename)
    sound = SOUND_CACHE.get(file_path, None)
    if not sound:
        if not os.path.exists(file_path):
            return
        SOUND_CACHE[file_path] = sound = pygame.mixer.Sound(file_path)
    sound.play()

CURRENT_MUSIC_FILE = None

def stop_background_music():
    """stops any playing background music"""
    global CURRENT_MUSIC_FILE
    if not (SOUND_INITIALIZED and config.sound):
        return
    CURRENT_MUSIC_FILE = None
    # TODO: fadeout in a background thread
    pygame.mixer.music.stop()

def background_music(filename):
    """plays the background music with the given filename from the data sounds directory"""
    global CURRENT_MUSIC_FILE
    if not (SOUND_INITIALIZED and config.sound):
        return
    file_path = data.filepath("sounds", filename)
    if CURRENT_MUSIC_FILE == file_path:
        return
    stop_background_music()
    if not os.path.exists(file_path):
        return
    CURRENT_MUSIC_FILE = file_path
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

