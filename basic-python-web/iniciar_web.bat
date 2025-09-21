@echo off
cd /d "%~dp0"

REM Activar entorno virtual (si existe)
IF EXIST "mi_entorno\Scripts\activate.bat" (
    call mi_entorno\Scripts\activate.bat
)

REM Abrir navegador automáticamente
start http://127.0.0.1:5000

REM Ejecutar la aplicación Flask como paquete
python -m app.main

pause
