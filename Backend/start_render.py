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

# Configurar variables de entorno críticas para producción
os.environ['FLASK_ENV'] = 'production'
os.environ['DEBUG'] = 'false'

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
        
        # Preparar variables de entorno para el proceso
        env = os.environ.copy()
        env['FLASK_ENV'] = 'production'
        env['DEBUG'] = 'false'
        
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
        
        # Iniciar proceso en background con variables de entorno
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,  # Pasar variables de entorno
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
    
    # Importar configuración de producción
    try:
        from config_production import production_config
        print(f"✅ Usando configuración de producción: {production_config.__class__.__name__}")
        print(f"🔗 URLs de servicios:")
        print(f"   Auth: {production_config.AUTH_SERVICE_URL}")
        print(f"   User: {production_config.USER_SERVICE_URL}")
        print(f"   Task: {production_config.TASK_SERVICE_URL}")
    except ImportError:
        print("⚠️  No se pudo importar config_production, usando puertos por defecto")
        production_config = None
    
    # En Render, los microservicios se ejecutan como servicios separados
    # Solo iniciamos el API Gateway
    print("ℹ️  En Render, los microservicios se ejecutan como servicios separados")
    print("ℹ️  Solo se iniciará el API Gateway")
    
    return []

def start_api_gateway():
    """Iniciar API Gateway en el puerto principal"""
    try:
        port = int(os.environ.get('PORT', 10000))
        print(f"🌐 Iniciando API Gateway en puerto {port}...")
        
        # Preparar variables de entorno para el proceso
        env = os.environ.copy()
        env['FLASK_ENV'] = 'production'
        env['DEBUG'] = 'false'
        
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
        print(f"   FLASK_ENV: {env.get('FLASK_ENV')}")
        print(f"   DEBUG: {env.get('DEBUG')}")
        
        # Ejecutar API Gateway (proceso principal) con variables de entorno
        subprocess.run(cmd, env=env)
        
    except Exception as e:
        print(f"❌ Error iniciando API Gateway: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    # Configurar manejador de señales
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 INICIANDO API GATEWAY EN RENDER")
    print("=" * 50)
    
    # Verificar MongoDB Atlas
    print("🔍 Verificando conexión a MongoDB Atlas...")
    if not check_mongodb_connection():
        print("❌ No se puede continuar sin conexión a MongoDB Atlas")
        sys.exit(1)
    
    # En Render, los microservicios se ejecutan como servicios separados
    # Solo iniciamos el API Gateway
    print("\nℹ️  En Render, los microservicios se ejecutan como servicios separados")
    print("ℹ️  Solo se iniciará el API Gateway")
    
    # Iniciar API Gateway (proceso principal)
    print("\n🌐 Iniciando API Gateway...")
    start_api_gateway()

if __name__ == "__main__":
    main()
