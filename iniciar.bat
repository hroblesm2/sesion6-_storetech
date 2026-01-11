@echo off
echo ========================================
echo   Tienda Virtual GPS - Inicio Rapido
echo ========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Por favor instale Python desde https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Verificando dependencias...
pip install -r requirements.txt --quiet

echo [2/3] Iniciando base de datos...
echo.

echo [3/3] Iniciando servidor...
echo.
echo ========================================
echo   Servidor iniciado exitosamente!
echo   Acceder en: http://localhost:5000
echo ========================================
echo.
echo Usuarios por defecto:
echo   Admin    - Usuario: admin    Password: admin123
echo   Asesor   - Usuario: asesor   Password: asesor123
echo.
echo Presione Ctrl+C para detener el servidor
echo.

python app.py

pause