@echo off
setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

REM Determine Python executable
if not defined PYTHON set PYTHON=python

REM Check if Python is available
where %PYTHON% >nul 2>&1
if errorlevel 1 (
    echo python is required but not found on PATH. Please install Python or set PYTHON to the correct executable.
    exit /b 1
)

REM Check if pip is available
%PYTHON% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip is not available for %PYTHON%. Please install pip for this Python interpreter.
    exit /b 1
)

REM Get user site directories
for /f "delims=" %%i in ('%PYTHON% -m site --user-base') do set "USER_BASE=%%i"
set "USER_BIN=%USER_BASE%\bin"
set "USER_SCRIPTS=%USER_BASE%\Scripts"

REM Add user directories to PATH if they exist
if exist "%USER_BIN%" (
    set "PATH=%USER_BIN%;!PATH!"
)
if exist "%USER_SCRIPTS%" (
    set "PATH=%USER_SCRIPTS%;!PATH!"
)

echo Using user site directories:
echo   %USER_BIN%
echo   %USER_SCRIPTS%

REM Check if uv is installed
where uv >nul 2>&1
if errorlevel 1 (
    echo uv is not installed. Installing uv into the user site-packages...
    %PYTHON% -m pip install uv
) else (
    echo uv is already installed.
)

echo Installing project dependencies into the user site-packages...
%PYTHON% -m pip install -r requirements.txt

echo Setup complete. Run the pipeline with:
echo   python -m etl.main

endlocal
