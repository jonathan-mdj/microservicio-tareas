#!/usr/bin/env python3
"""
Script principal para iniciar todos los microservicios en Render
"""
import os
import sys
import subprocess
import time
import threading
from dotenv import load_dotenv

# Cargar variables de entorno para producción
if os.path.exists('.env.atlas'):
    load_dotenv('.env.atlas')

def start_service(service_name, port):
    """Iniciar un microservicio individual"""
    try:
        print(f"🚀 Iniciando {service_name} en puerto {port}...")
        
        # Comando para cada servicio usando gunicorn
        cmd = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '1',
            '--timeout', '120',
            f'{service_name}.app_mongo:app'  # Usar la versión MongoDB
        ]
        
        # Iniciar proceso
        process = subprocess.Popen(
            cmd,
            cwd='/opt/render/project/src/Backend',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✅ {service_name} iniciado con PID {process.pid}")
        return process
        
    except Exception as e:
        print(f"❌ Error iniciando {service_name}: {e}")
        return None

def start_all_services():
    """Iniciar todos los microservicios"""
    services = [
        ('auth_service', 5001),
        ('user_service', 5002), 
        ('task_service', 5003)
    ]
    
    processes = []
    
    for service_name, port in services:
        process = start_service(service_name, port)
        if process:
            processes.append((service_name, process))
        time.sleep(2)  # Esperar entre servicios
    
    return processes

def start_api_gateway():
    """Iniciar API Gateway en el puerto principal"""
    try:
        port = int(os.environ.get('PORT', 10000))  # Render usa PORT
        print(f"🌐 Iniciando API Gateway en puerto {port}...")
        
        cmd = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '2',
            '--timeout', '120',
            'api_gateway.app_mongo:app'  # Usar versión MongoDB
        ]
        
        # Ejecutar API Gateway
        subprocess.run(cmd, cwd='/opt/render/project/src/Backend')
        
    except Exception as e:
        print(f"❌ Error iniciando API Gateway: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("🚀 INICIANDO MICROSERVICIOS EN RENDER...")
    print("=" * 50)
    
    # 1. Iniciar microservicios en background
    processes = start_all_services()
    
    # 2. Dar tiempo a que inicien
    print("⏳ Esperando a que los servicios inicien...")
    time.sleep(10)
    
    # 3. Iniciar API Gateway (proceso principal)
    start_api_gateway()
