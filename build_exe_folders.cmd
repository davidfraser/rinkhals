@echo off

echo PHASE 1: Determining paths
for /F "tokens=* USEBACKQ" %%F in (`python -c "from gamelib import version as v; print(f'orcassault-{v.VERSION_STR}')"`) do (
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
set TARGET_ARCHIVE=dist\%TARGET_NAME%-win
if exist %TARGET_ARCHIVE%.zip (
    if "%1" equ "/y" (
        echo %TARGET_ARCHIVE%.zip already exists - removing to recreate as running with /y
        del %TARGET_ARCHIVE%.zip
    ) else (
        echo %TARGET_ARCHIVE%.zip already exists - stopping so as not to overwrite unintentionally >&2
        echo To suppress this check, run with /y >&2
        exit /b 1
    )
)
if exist %TARGET_DIR% (
    echo %TARGET_DIR% exists: removing to make clean build
    rd /s /q %TARGET_DIR%
    mkdir %TARGET_DIR%
)

echo PHASE 2: Running pyexebuilder
rem pyexebuilder needs these in the current directory, but we'll delete them just now
copy /y %BASE_PYTHON_DIR%\python3*.dll .
python -m pyexebuilder.ExeBuilder --module-name run_game --module-exe-name orcassault --dest-dir=venv\ --icon data\icons\orcassault.ico
rem we put the exe and dlls into venv so the paths end up coming out right - but we don't need them there
copy /y venv\orcassault.exe %TARGET_DIR%\
del venv\orcassault.exe venv\python3*.dll
copy /y python3*.dll %TARGET_DIR%\
del python3*.dll

echo PHASE 3: Copying necessary files
copy /y fix_exe_paths.py %TARGET_DIR%\_tkinter.py
copy /y run_game.py %TARGET_DIR%\
copy /y README.md %TARGET_DIR%\README.txt
copy /y COPYING %TARGET_DIR%\COPYING.txt
copy /y COPYRIGHT %TARGET_DIR%\COPYRIGHT.txt
xcopy /e /q /y %BASE_PYTHON_DIR%\Lib\ %TARGET_DIR%\Lib\
xcopy /e /q /y %BASE_PYTHON_DIR%\DLLs\ %TARGET_DIR%\DLLs\
xcopy /e /q /y venv\ %TARGET_DIR%\
xcopy /e /q /y gamelib\ %TARGET_DIR%\gamelib\
xcopy /e /q /y data\ %TARGET_DIR%\data\

echo PHASE 4: Removing unnecessary files
rd /s /q %TARGET_DIR%\Lib\test\
del %TARGET_DIR%\pyvenv.cfg

echo PHASE 5: Zipping
python -c "import shutil ; from os import getenv as e; shutil.make_archive(e('TARGET_ARCHIVE'), 'zip', root_dir=e('TARGET_DIR'))"
dir %TARGET_ARCHIVE%.zip

set BASE_PYTHON_DIR=
set VENV_PYTHON_DIR=
set TARGET_ARCHIVE=
set TARGET_NAME=
set TARGET_DIR=
