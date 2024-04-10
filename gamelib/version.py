"""Operation Fox Assault Version Information"""

VERSION = (1, 6, 0, 'alpha', 1)
BASE_VERSION_STR = '.'.join([str(x) for x in VERSION[:3]])
VERSION_STR = {
    'final': BASE_VERSION_STR,
    'alpha': BASE_VERSION_STR + 'a' + str(VERSION[4]),
    'rc': BASE_VERSION_STR + 'rc' + str(VERSION[4]),
}[VERSION[3]]

# incremement whenever a change breaks the save game file format
SAVE_GAME_VERSION = 2

NAME = 'Operation Fox Assault'
DESCRIPTION = 'Turn-based strategy game written using Pygame.'

PEOPLE = {
    'Simon': ('Simon Cross', 'hodgestar+rinkhals@gmail.com'),
    'Neil': ('Neil Muller', 'drnmuller+rinkhals@gmail.com'),
    'Adrianna': ('Adrianna Pinska', 'adrianna.pinska+rinkhals@gmail.com'),
    'Jeremy': ('Jeremy Thurgood', 'firxen+rinkhals@gmail.com'),
    'David': ('David Fraser', 'davidroyfraser+rinkhals@gmail.com'),
}

AUTHORS = [
    PEOPLE['Simon'],
    PEOPLE['Neil'],
    PEOPLE['Adrianna'],
    PEOPLE['Jeremy'],
    PEOPLE['David'],
]

AUTHOR_NAME = AUTHORS[0][0]
AUTHOR_EMAIL = AUTHORS[0][1]

MAINTAINERS = AUTHORS

MAINTAINER_NAME = MAINTAINERS[0][0]
MAINTAINER_EMAIL = MAINTAINERS[0][1]

ARTISTS = [
    PEOPLE['Adrianna'],
    PEOPLE['Jeremy'],
]

DOCUMENTERS = [
    PEOPLE['Neil'],
]

# SOURCEFORGE_URL = 'http://sourceforge.net/projects/XXXX/'
# PYPI_URL = 'http://pypi.python.org/pypi/XXXX/'

LICENSE = 'GPL'
# LICENSE_TEXT = resource_string(__name__, 'COPYING')

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: MacOS X',
    'Environment :: Win32 (MS Windows)',
    'Environment :: X11 Applications',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Topic :: Games/Entertainment :: Turn Based Strategy',
]

PLATFORMS = [
    'Linux',
    'Mac OS X',
    'Windows',
]

INSTALL_REQUIRES = [
]

# Install these manually
NON_EGG_REQUIREMENTS = [
    'setuptools',
    'pygame',
    'pgu',
]
