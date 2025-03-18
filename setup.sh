#!/bin/bash

echo "Configurando Spam Detector..."

# Crear entorno virtual
echo "Creando entorno virtual..."
python -m venv venv

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Crear carpeta uploads
echo "Creando carpeta uploads..."
mkdir -p uploads

echo "¡Configuración completada!"
echo "Para ejecutar la aplicación: source venv/bin/activate && python app.py"