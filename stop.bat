@echo off
REM Windows Batch File to Stop GK Video Generator

echo.
echo ========================================
echo   GK VIDEO GENERATOR - SHUTDOWN
echo ========================================
echo.

where wsl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WSL not found!
    pause
    exit /b 1
)

echo Stopping services in WSL...
echo.

REM Get the current directory path
set CURRENT_DIR=%~dp0
set CURRENT_DIR=%CURRENT_DIR:\=/%

REM Convert Windows path to WSL path
for /f "tokens=*" %%i in ('wsl wslpath "%CURRENT_DIR:~0,-1%"') do set WSL_PATH=%%i

REM Run the stop script in WSL
wsl cd "%WSL_PATH%" ^&^& chmod +x stop.sh ^&^& ./stop.sh

echo.
echo All services stopped!
echo.
pause
