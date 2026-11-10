@echo off
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 goto use_py

where python >nul 2>nul
if %errorlevel%==0 goto use_python

echo Chybi Python 3. Nainstaluj Python 3 a pri instalaci zapni volbu "Add Python to PATH".
pause
exit /b 1

:use_py
py -3 server.py
goto finished

:use_python
python server.py

:finished
if errorlevel 1 pause
