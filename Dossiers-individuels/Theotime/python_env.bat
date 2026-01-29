@echo off
REM === Chemins Python 3 (à adapter si nécessaire) ===
set PYTHON_DIR=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311
set PYTHON_SCRIPTS=%PYTHON_DIR%\Scripts

REM === Ajout temporaire au PATH ===
set PATH=%PYTHON_DIR%;%PYTHON_SCRIPTS%;%PATH%

REM === Vérification ===
echo Python utilise :
python --version
echo.

REM === Se deplace vers l'initialisation de l'environnement virtuel ===
cd Simulation_banc\simulation_banc_mpy

REM === demarre l'environnement virtuel ===
CALL setup_esptool.bat

pip install mpy-cross==1.27.0.post2

REM === Ouvre un terminal interactif ===

cd ../simulation_esp

cmd