#!/bin/bash

echo "========================================"
echo "INICIANDO FRONTEND - TASK MANAGER"
echo "========================================"
echo

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js no está instalado o no está en el PATH"
    echo "Por favor instala Node.js desde https://nodejs.org/"
    exit 1
fi

# Verificar si Angular CLI está instalado
if ! command -v ng &> /dev/null; then
    echo "ERROR: Angular CLI no está instalado"
    echo "Instalando Angular CLI globalmente..."
    npm install -g @angular/cli
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudo instalar Angular CLI"
        exit 1
    fi
fi

# Verificar si las dependencias están instaladas
if [ ! -d "node_modules" ]; then
    echo "Instalando dependencias..."
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudieron instalar las dependencias"
        exit 1
    fi
fi

echo
echo "========================================"
echo "CONFIGURACIÓN COMPLETADA"
echo "========================================"
echo
echo "Asegúrate de que el backend esté ejecutándose:"
echo "- API Gateway: http://localhost:4000"
echo "- Auth Service: http://localhost:5001"
echo "- Task Service: http://localhost:5003"
echo
echo "Iniciando servidor de desarrollo..."
echo

# Iniciar el servidor de desarrollo
ng serve --open

echo
echo "Servidor detenido." 