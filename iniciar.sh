#!/bin/bash

echo "========================================"
echo "  Tienda Virtual GPS - Inicio Rápido"
echo "========================================"
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    echo "Por favor instale Python 3"
    exit 1
fi

echo "[1/3] Verificando dependencias..."
pip3 install -r requirements.txt --quiet

echo "[2/3] Iniciando base de datos..."
echo ""

echo "[3/3] Iniciando servidor..."
echo ""
echo "========================================"
echo "  Servidor iniciado exitosamente!"
echo "  Acceder en: http://localhost:5000"
echo "========================================"
echo ""
echo "Usuarios por defecto:"
echo "  Admin    - Usuario: admin    Password: admin123"
echo "  Asesor   - Usuario: asesor   Password: asesor123"
echo ""
echo "Presione Ctrl+C para detener el servidor"
echo ""

python3 app.py