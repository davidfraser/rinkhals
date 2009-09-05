# setup.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4

"""Setuptools setup.py file for Operation Fox Assault."""

from setuptools import setup, find_packages
from gamelib import version

try:
    import py2exe
    from py2exe.build_exe import py2exe as builder
    import os
    import glob

    class PkgResourceBuilder(builder):
        def copy_extensions(self, extensions):
            """Hack the py2exe C extension copier
               to put pkg_resources into the
               library.zip file.
               """
            builder.copy_extensions(self, extensions)
            package_data = self.distribution.package_data.copy()

            for package, patterns in self.distribution.package_data.items():
                package_dir = os.path.join(*package.split('.'))
                collect_dir = os.path.join(self.collect_dir, package_dir)

                # create sub-dirs in py2exe collection area
                # Copy the media files to the collection dir.
                # Also add the copied file to the list of compiled
                # files so it will be included in zipfile.
                for pattern in patterns:
                    pattern = os.path.join(*pattern.split('/'))
                    for f in glob.glob(os.path.join(package_dir, pattern)):
                        name = os.path.basename(f)
                        folder = os.path.join(collect_dir, os.path.dirname(f))
                        if not os.path.exists(folder):
                            self.mkpath(folder)
                        self.copy_file(f, os.path.join(collect_dir, name))
                        self.compiled_files.append(os.path.join(package_dir, name))

except ImportError:
    PkgResourceBuilder = None

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
            package_data = {
                # NOTE: PkgResourceBuilder cannot handle the
                #   catch-all empty package ''.
                # Include SVG files from sutekh.gui package
                #'sutekh.gui': ['*.svg'],
                # Include LICENSE information for sutekh package
                # Include everything under the docs directory
                #'sutekh': ['COPYING', 'docs/html/*'],
            },
            scripts = ['scripts/foxassault.py','scripts/testconsole.py'],

            # py2exe
            console = ['scripts/testconsole.py'],
            windows = [{
                'script': 'scripts/foxassault.py',
                # 'icon_resources': [(0, "artwork/sutekh-icon-inkscape.ico")],
            }],
            cmdclass = {
                'py2exe': PkgResourceBuilder,
            },
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
            }},
            data_files = [
                'COPYRIGHT',
                'COPYING',
            ],
        )
