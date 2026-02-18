@echo off
REM Windows Batch File to Start GK Video Generator
REM This launches the bash script in WSL

echo.
echo ========================================
echo   GK VIDEO GENERATOR - STARTUP
echo ========================================
echo.

REM Check if running in WSL
where wsl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WSL not found!
    echo Please install WSL first.
    echo.
    pause
    exit /b 1
)

echo Starting services in WSL...
echo.

REM Get the current directory path
set CURRENT_DIR=%~dp0
set CURRENT_DIR=%CURRENT_DIR:\=/%

REM Convert Windows path to WSL path
for /f "tokens=*" %%i in ('wsl wslpath "%CURRENT_DIR:~0,-1%"') do set WSL_PATH=%%i

REM Run the startup script in WSL
wsl cd "%WSL_PATH%" ^&^& chmod +x start.sh ^&^& ./start.sh

echo.
echo Press any key to exit...
pause >nul
