@echo off

echo PHASE 1: Determining paths
FOR /F "tokens=* USEBACKQ" %%F IN (`python -c "from gamelib import version as v; print(f'foxassault-{v.VERSION_STR}')"`) DO (
  SET TARGET_NAME=%%F
)
FOR /F "tokens=* USEBACKQ" %%F IN (`python -c "import sys ; print(sys.base_prefix)"`) DO (
  SET BASE_PYTHON_DIR=%%F
)
FOR /F "tokens=* USEBACKQ" %%F IN (`python -c "import sys ; print(sys.prefix)"`) DO (
  SET VENV_PYTHON_DIR=%%F
)
set TARGET_DIR=dist\%TARGET_NAME%
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
