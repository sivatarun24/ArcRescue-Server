@echo off

if not exist "arcgis-env" (
    echo Creating virtual environment...
    python -m venv arcgis-env
)

call arcgis-env\Scripts\activate.bat

pip install -r requirements.txt
pip list | findstr arcgis >nul
if errorlevel 1 (
    echo Installing arcgis package...
    pip install arcgis
) else (
    echo arcgis already installed.
)


@REM how to run: .\setup_arcgis_env.bat
