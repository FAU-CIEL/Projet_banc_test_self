@echo off
REM ------------------------------
REM Setup ESPTool Virtual Env
REM ------------------------------

REM Nom du dossier de l'environnement virtuel
set VENV_NAME=esptoolenv

REM Crée l'environnement virtuel
echo Creating Python virtual environment...
python3 -m venv %VENV_NAME%
if errorlevel 1 (
    echo Failed to create virtual environment. Make sure Python is installed and in your PATH.
    pause
    exit /b 1
)

REM Active l'environnement virtuel
echo Activating virtual environment...
call %VENV_NAME%\Scripts\activate

REM Vérifie que l'activation a fonctionné
if not defined VIRTUAL_ENV (
    echo Virtual environment activation failed.
    pause
    exit /b 1
)

REM Installe esptool dans l'env virtuel
echo Installing esptool...
pip install --upgrade pip
pip install esptool

if errorlevel 1 (
    echo Failed to install esptool.
    pause
    exit /b 1
)

echo.
echo ================================
echo esptool environment ready!
echo To use it, run this batch file and then:
echo    esptool --help
echo.
echo To deactivate, type: deactivate
echo ================================
