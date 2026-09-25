@echo off
chcp 65001 > nul
cls
echo ============================================================
echo   ☁️ CLOUDOPS DASHBOARD - SIMULADOR DE SUCESIONES RECURSIVAS
echo   📚 Matemática Discreta - Tema 04: Sucesiones y Recurrencias
echo ============================================================
echo.

echo [1/3] Verificando instalación de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado o no se encuentra en el PATH.
    echo Por favor instale Python 3.10 o superior para continuar.
    pause
    exit /b 1
)

echo [2/3] Verificando librerías requeridas (Flask, SymPy, NumPy)...
python -c "import flask, sympy, numpy" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Instalando dependencias desde requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Ocurrió un error al instalar las dependencias.
        pause
        exit /b 1
    )
)

echo [3/3] Iniciando Servidor Flask y abriendo interfaz web...
echo 📡 Servidor corriendo en: http://127.0.0.1:5000
echo 💡 Presione CTRL+C en esta consola para detener el servidor.
echo.

:: Esperar 1.5 segundos e iniciar el navegador por defecto
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

:: Arrancar la aplicación Flask
python app.py

pause
