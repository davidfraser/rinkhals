# This is copied into the target folder by build_exe_folders.cmd, to fix up the paths set by pyexebuilder
# It's copied as _tkinter.py which it isn't, and would prevent any tk-based code from working properly
# But we don't use tkinter

import sys
import os
from os.path import abspath, dirname, join
script_dir = dirname(abspath(__file__))

dlls_dir = join(script_dir, 'DLLs')
libs_dir = join(script_dir, 'Lib')
site_packages_dir = join(script_dir, 'Lib', 'site-packages')

os.add_dll_directory(dlls_dir)
sys.path.append(dlls_dir)
sys.path.append(libs_dir)
sys.path.append(site_packages_dir)
