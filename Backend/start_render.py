#!/usr/bin/env python3
"""
Script simplificado para iniciar servicios en Render
"""
import os
import sys
import subprocess
import time
import signal
from dotenv import load_dotenv

# Cargar variables de entorno para producción
if os.path.exists('.env.atlas'):
    load_dotenv('.env.atlas')

def signal_handler(signum, frame):
    """Manejar señales de terminación"""
    print(f"\n🛑 Señal {signum} recibida. Cerrando servicios...")
    sys.exit(0)

def check_mongodb_connection():
    """Verificar conexión a MongoDB Atlas"""
    try:
        from database_mongo_render import mongo_db
        connected = mongo_db.connect()
        if connected:
            print("✅ Conexión a MongoDB Atlas exitosa")
            return True
        else:
            print("❌ No se pudo conectar a MongoDB Atlas")
            return False
    except Exception as e:
        print(f"❌ Error verificando MongoDB: {e}")
        return False

def start_service_with_gunicorn(service_name, port, workers=1):
    """Iniciar un servicio usando gunicorn"""
    try:
        print(f"🚀 Iniciando {service_name} en puerto {port}...")
        
        cmd = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', str(workers),
            '--timeout', '120',
            '--keep-alive', '5',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            f'{service_name}.app_mongo:app'
        ]
        
        # Iniciar proceso en background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Crear nuevo grupo de procesos
        )
        
        print(f"✅ {service_name} iniciado con PID {process.pid}")
        return process
        
    except Exception as e:
        print(f"❌ Error iniciando {service_name}: {e}")
        return None

def start_all_services():
    """Iniciar todos los microservicios"""
    print("🔧 Iniciando microservicios...")
    
    services = [
        ('auth_service', 5001, 1),
        ('user_service', 5002, 1),
        ('task_service', 5003, 1)
    ]
    
    processes = []
    
    for service_name, port, workers in services:
        process = start_service_with_gunicorn(service_name, port, workers)
        if process:
            processes.append((service_name, process))
        time.sleep(3)  # Esperar entre servicios
    
    return processes

def start_api_gateway():
    """Iniciar API Gateway en el puerto principal"""
    try:
        port = int(os.environ.get('PORT', 10000))
        print(f"🌐 Iniciando API Gateway en puerto {port}...")
        
        cmd = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '2',
            '--timeout', '120',
            '--keep-alive', '5',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--access-logfile', '-',
            '--error-logfile', '-',
            'api_gateway.app_mongo:app'
        ]
        
        print("🚀 API Gateway iniciado con gunicorn")
        print(f"   URL: http://0.0.0.0:{port}")
        print(f"   Health Check: http://0.0.0.0:{port}/health")
        print("   Logs: stdout/stderr")
        
        # Ejecutar API Gateway (proceso principal)
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Error iniciando API Gateway: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    # Configurar manejador de señales
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 INICIANDO MICROSERVICIOS EN RENDER")
    print("=" * 50)
    
    # Verificar MongoDB Atlas
    print("🔍 Verificando conexión a MongoDB Atlas...")
    if not check_mongodb_connection():
        print("❌ No se puede continuar sin conexión a MongoDB Atlas")
        sys.exit(1)
    
    # Iniciar microservicios en background
    print("\n🔧 Iniciando microservicios...")
    processes = start_all_services()
    
    if not processes:
        print("❌ No se pudo iniciar ningún microservicio")
        sys.exit(1)
    
    # Dar tiempo a que los servicios inicien
    print(f"\n⏳ Esperando a que {len(processes)} servicios inicien...")
    time.sleep(15)
    
    # Verificar que los servicios estén funcionando
    print("🔍 Verificando estado de servicios...")
    for service_name, process in processes:
        if process.poll() is None:  # Proceso aún ejecutándose
            print(f"   ✅ {service_name}: Ejecutándose (PID: {process.pid})")
        else:
            print(f"   ❌ {service_name}: Terminado prematuramente")
    
    # Iniciar API Gateway (proceso principal)
    print("\n🌐 Iniciando API Gateway...")
    start_api_gateway()

if __name__ == "__main__":
    main()
