#!/bin/bash

# Script de inicio para el Stock Analyzer
echo "🚀 Iniciando Stock Analyzer Pro..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está instalado"
    exit 1
fi

# Instalar dependencias si no existen
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar/actualizar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Verificar que streamlit está instalado
if ! command -v streamlit &> /dev/null; then
    echo "❌ Error: Streamlit no se instaló correctamente"
    exit 1
fi

# Ejecutar aplicación
echo "🎯 Iniciando aplicación en http://localhost:8501"
streamlit run app.py