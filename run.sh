#!/usr/bin/env bash

# ============================================================
#   ☁️ CLOUDOPS DASHBOARD - SIMULADOR DE SUCESIONES RECURSIVAS
#   📚 Matemática Discreta - Tema 04: Sucesiones y Recurrencias
# ============================================================

echo "============================================================"
echo "  ☁️ CLOUDOPS DASHBOARD - SIMULADOR DE SUCESIONES RECURSIVAS"
echo "  📚 Matemática Discreta - Tema 04: Sucesiones y Recurrencias"
echo "============================================================"
echo ""

# 1. Comprobar Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 no se encuentra instalado en el sistema."
    exit 1
fi

# 2. Comprobar dependencias
python3 -c "import flask, sympy, numpy" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[INFO] Instalando dependencias de Python..."
    pip install -r requirements.txt
fi

echo "[INFO] Iniciando Servidor Flask..."
echo "📡 Servidor activo en: http://127.0.0.1:5000"

# 3. Abrir navegador automáticamente
if which xdg-open > /dev/null; then
    (sleep 1.5 && xdg-open http://127.0.0.1:5000) &
elif which open > /dev/null; then
    (sleep 1.5 && open http://127.0.0.1:5000) &
fi

# 4. Iniciar Flask
python3 app.py
