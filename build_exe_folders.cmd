@echo off

echo PHASE 1: Determining paths
for /F "tokens=* USEBACKQ" %%F in (`python -c "from gamelib import version as v; print(f'foxassault-{v.VERSION_STR}')"`) do (
  set TARGET_NAME=%%F
)
for /F "tokens=* USEBACKQ" %%F in (`python -c "import sys ; print(sys.base_prefix)"`) do (
  set BASE_PYTHON_DIR=%%F
)
for /F "tokens=* USEBACKQ" %%F in (`python -c "import sys ; print(sys.prefix)"`) do (
  set VENV_PYTHON_DIR=%%F
)
set TARGET_DIR=dist\%TARGET_NAME%
if not exist dist (mkdir dist)
if exist %TARGET_DIR% (rd /s /q %TARGET_DIR% & mkdir %TARGET_DIR%)

echo PHASE 2: Running pyexebuilder
rem pyexebuilder needs these in the current directory, but we'll delete them just now
copy /y %BASE_PYTHON_DIR%\python3*.dll .
python -m pyexebuilder.ExeBuilder --module-name run_game --module-exe-name fox-assault --dest-dir=venv\ --icon data\icons\foxassault.ico
rem we put the exe and dlls into venv so the paths end up coming out right - but we don't need them there
copy /y venv\fox-assault.exe %TARGET_DIR%\
del venv\fox-assault.exe venv\python3*.dll
copy /y python3*.dll %TARGET_DIR%\
del python3*.dll

echo PHASE 3: Copying necessary files
copy /y fix_exe_paths.py %TARGET_DIR%\_tkinter.py
copy /y run_game.py %TARGET_DIR%\
xcopy /e /q /y %BASE_PYTHON_DIR%\Lib\ %TARGET_DIR%\Lib\
xcopy /e /q /y %BASE_PYTHON_DIR%\DLLs\ %TARGET_DIR%\DLLs\
xcopy /e /q /y venv\ %TARGET_DIR%\
xcopy /e /q /y gamelib\ %TARGET_DIR%\gamelib\
xcopy /e /q /y data\ %TARGET_DIR%\data\

echo PHASE 4: Removing unnecessary files
rd /s /q %TARGET_DIR%\Lib\test\

echo PHASE 5: Zipping
set TARGET_ARCHIVE=dist\%TARGET_NAME%
python -c "import shutil ; from os import getenv as e; shutil.make_archive(e('TARGET_ARCHIVE'), 'zip', base_dir=e('TARGET_DIR'))"
dir %TARGET_ARCHIVE%.zip

set BASE_PYTHON_DIR=
set VENV_PYTHON_DIR=
set TARGET_ARCHIVE=
set TARGET_NAME=
set TARGET_DIR=
