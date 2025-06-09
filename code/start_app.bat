@echo off
ECHO =======================================================
ECHO  Starting WOCIAO Project Services...
ECHO =======================================================

ECHO.
ECHO  Launching Flask Backend Server (API Service)...
start "Flask Server" cmd /k "python app.py"

ECHO.
ECHO  Launching Jupyter Lab Server (Dashboard Service)...
start "Jupyter Dashboard" cmd /k "jupyter lab --port 8888"

ECHO.
ECHO =======================================================
ECHO  All services have been launched in new windows.
ECHO  You can now open your browser to http://127.0.0.1:5000
ECHO  This window will close automatically.
ECHO =======================================================

timeout /t 5 >nul
exit