'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''

import os

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))

def unix_to_local(filename):
    '''Convert a relative unix / http filename to a local one.'''
    return os.path.join(*filename.split("/"))

def filepath(*filenames):
    '''Determine the path to a file in the data directory.
    '''
    os_filenames = [unix_to_local(f) for f in filenames]
    return os.path.join(data_dir, *os_filenames)

def load(filename, mode='rb'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    # convert unix path separator to platform appropriate one
    filename = unix_to_local(filename)
    return open(os.path.join(data_dir, filename), mode)

