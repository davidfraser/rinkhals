# setup.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4

"""Setuptools setup.py file for Operation Fox Assault."""

from setuptools import setup, find_packages
from gamelib import version

try:
    import py2exe
except ImportError:
    pass

setup   (   # Metadata
            name = version.NAME,
            version = version.VERSION_STR,
            description = version.DESCRIPTION,

            author = version.AUTHOR_NAME,
            author_email = version.AUTHOR_EMAIL,

            maintainer = version.MAINTAINER_NAME,
            maintainer_email = version.MAINTAINER_EMAIL,

            # url = version.SOURCEFORGE_URL,
            # download_url = version.PYPI_URL,

            license = version.LICENSE,

            classifiers = version.CLASSIFIERS,

            platforms = version.PLATFORMS,

            # Dependencies
            install_requires = version.INSTALL_REQUIRES,

            # Files
            packages = find_packages(),
            scripts = ['scripts/foxassault.py', 'scripts/testconsole.py'],

            # py2exe
            console = ['scripts/testconsole.py'],
            windows = [{
                'script': 'scripts/foxassault.py',
                'icon_resources': [(0, "data/icons/foxassault.ico")],
            }],
            app = ['scripts/foxassault.py'],
            options = { 'py2exe': {
                'skip_archive': 1,
                'dist_dir': 'dist/foxassault-%s' % version.VERSION_STR,
                'packages': [
                    'logging', 'encodings',
                ],
                'includes': [
                    # pygame
                    'pygame', 'pgu',
                ],
                'excludes': [
                    'numpy',
                ],
                'ignores': [
                    # all database modules
                    'pgdb', 'Sybase', 'adodbapi',
                    'kinterbasdb', 'psycopg', 'psycopg2', 'pymssql',
                    'sapdb', 'pysqlite2', 'sqlite', 'sqlite3',
                    'MySQLdb', 'MySQLdb.connections',
                    'MySQLdb.constants.CR', 'MySQLdb.constants.ER',
                    # old datetime equivalents
                    'DateTime', 'DateTime.ISO',
                    'mx', 'mx.DateTime', 'mx.DateTime.ISO',
                    # email modules
                    'email.Generator', 'email.Iterators', 'email.Utils',
                ],
            },
            'py2app': {
                'argv_emulation': 1,
                'iconfile': 'data/icons/foxassault.icns',
#                 'dist_dir': 'dist/foxassault-%s' % version.VERSION_STR,
#                 'bdist_base': 'build/bdist',
                'packages': [
                    'logging', 'encodings', 'pygame', 'pgu', 'gamelib', 'data',
                ],
                'excludes': ['numpy'],
            }},
            data_files = [
                ['', ['COPYRIGHT', 'COPYING', 'README.txt']],
            ],
        )
