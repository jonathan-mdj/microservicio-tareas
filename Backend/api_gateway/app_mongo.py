# api_gateway/app_mongo.py
from flask import Flask, jsonify, request, g
import requests
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from requests.exceptions import ConnectionError, Timeout, RequestException
import logging
import os
import json
from datetime import datetime
import time
import jwt
from logging.handlers import RotatingFileHandler

# Importar configuración según el entorno
if os.getenv('FLASK_ENV') == 'production':
    from config_production import production_config as config
    print("🚀 [GATEWAY] Usando configuración de PRODUCCIÓN")
else:
    from config import config
    print("🔧 [GATEWAY] Usando configuración de DESARROLLO")

app = Flask(__name__)

# Configuración de logging básico y seguro
LOG_DIR = 'logs'
LOG_FILE = 'logs/api_gateway_mongo.log'

# Crear directorio de logs si no existe
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configurar logger básico
def setup_logger():
    """Configurar el logger para escribir logs en archivo"""
    logger = logging.getLogger('api_gateway_mongo')
    logger.setLevel(logging.INFO)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Agregar handler al logger
    logger.addHandler(file_handler)
    
    return logger

# Inicializar logger
logger = setup_logger()

# Configuración de Rate Limiting para protección contra ataques
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute", "1000 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Configuración CORS más específica y robusta
print(f"🌐 [GATEWAY] Configurando CORS con origins: {config.CORS_ORIGINS}")
CORS(app, 
     origins=config.CORS_ORIGINS,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=True,
     max_age=3600)

# URLs de los microservicios MongoDB
AUTH_SERVICE_URL = f'http://localhost:{config.AUTH_SERVICE_PORT}'
USER_SERVICE_URL = f'http://localhost:{config.USER_SERVICE_PORT}'
TASK_SERVICE_URL = f'http://localhost:{config.TASK_SERVICE_PORT}'

print(f"[GATEWAY] URLs de servicios MongoDB:")
print(f"   Auth Service: {AUTH_SERVICE_URL}")
print(f"   User Service: {USER_SERVICE_URL}")
print(f"   Task Service: {TASK_SERVICE_URL}")

# Función para extraer información del usuario del token JWT
def extract_user_from_token():
    """Extraer información del usuario del token JWT de manera segura"""
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # Decodificar token (sin verificar para extraer info)
            payload = jwt.decode(token, options={"verify_signature": False})
            return {
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'role_id': payload.get('role_id')
            }
    except Exception as e:
        logger.warning(f"Error extrayendo usuario del token: {e}")
    
    return None

# Función para registrar petición de API de manera segura
def log_api_request():
    """Registrar información de la petición entrante de manera segura"""
    try:
        g.start_time = time.time()
        
        user_info = extract_user_from_token()
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "endpoint": getattr(request, 'endpoint', 'unknown'),
            "path": request.path,
            "url": request.url,
            "user_agent": request.headers.get('User-Agent', 'N/A'),
            "ip_address": request.remote_addr,
            "user": user_info
        }
        
        logger.info(f"REQUEST_START: {json.dumps(log_data)}")
    except Exception as e:
        logger.error(f"Error en log_api_request: {e}")
        # No fallar si hay error en logging

# Función para registrar respuesta de API de manera segura
def log_api_response(response):
    """Registrar información de la respuesta saliente de manera segura"""
    try:
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time
            response_time_ms = round(response_time * 1000, 2)
            response_time_seconds = round(response_time, 3)
        else:
            response_time_ms = 0
            response_time_seconds = 0
        
        # Determinar el servicio basado en la ruta
        service_name = "api_gateway"
        if request.path.startswith('/auth/'):
            service_name = "auth_service_mongo"
        elif request.path.startswith('/user/'):
            service_name = "user_service_mongo"
        elif request.path.startswith('/task/'):
            service_name = "task_service_mongo"
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "endpoint": getattr(request, 'endpoint', 'unknown'),
            "path": request.path,
            "service": service_name,
            "status_code": response.status_code,
            "response_time_ms": response_time_ms,
            "response_time_seconds": response_time_seconds,
            "content_length": getattr(response, 'content_length', 0)
        }
        
        logger.info(f"RESPONSE_END: {json.dumps(log_data)}")
    except Exception as e:
        logger.error(f"Error en log_api_response: {e}")
        # No fallar si hay error en logging
    
    return response

# Middleware para registrar peticiones de manera segura
@app.before_request
def before_request():
    """Middleware que se ejecuta antes de cada petición"""
    log_api_request()

# Middleware para registrar respuestas de manera segura
@app.after_request
def after_request(response):
    """Middleware que se ejecuta después de cada petición"""
    return log_api_response(response)

def proxy_request(service_url, path):
    """Función auxiliar para hacer proxy de requests"""
    url = f"{service_url}/{path}"
    
    headers = {}
    for key, value in request.headers:
        if key.lower() not in ['host', 'content-length', 'connection']:
            headers[key] = value
    
    try:
        # Agregar headers específicos para evitar problemas
        if 'Content-Type' not in headers and request.is_json:
            headers['Content-Type'] = 'application/json'
        
        # Rate limiting más estricto para operaciones de escritura
        if request.method in ['POST', 'PUT', 'DELETE']:
            # Verificar límites adicionales para operaciones críticas
            pass
        
        resp = requests.request(
            method=request.method,
            url=url,
            json=request.get_json() if request.is_json else None,
            headers=headers,
            timeout=30,
            allow_redirects=False
        )
        
        # Crear respuesta con headers CORS apropiados
        try:
            response_data = resp.json()
            response = jsonify(response_data)
        except ValueError:
            response = jsonify({"message": resp.text})
        
        response.status_code = resp.status_code
        
        # Agregar headers CORS explícitamente
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response
            
    except ConnectionError:
        error_response = jsonify({"error": "Servicio no disponible"})
        error_response.status_code = 503
        error_response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
        return error_response
    except Timeout:
        error_response = jsonify({"error": "Timeout del servicio"})
        error_response.status_code = 504
        error_response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
        return error_response
    except RequestException as e:
        error_response = jsonify({"error": f"Error en la solicitud: {str(e)}"})
        error_response.status_code = 500
        error_response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
        return error_response

# Manejo de errores para rate limiting
@app.errorhandler(429)  # Too Many Requests
def ratelimit_handler(e):
    """Manejar errores de rate limiting"""
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Demasiadas peticiones. Intenta de nuevo más tarde.",
        "retry_after": e.description if hasattr(e, 'description') else None
    }), 429

# Manejo explícito de OPTIONS para todas las rutas
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_preflight(path):
    """Manejar peticiones preflight OPTIONS para todas las rutas"""
    response = jsonify({'message': 'OK'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type', 'Authorization', 'X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

@app.route('/auth/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@limiter.limit("30 per minute")  # Límite más estricto para autenticación
def auth_proxy(path):
    """Proxy para el servicio de autenticación MongoDB"""
    return proxy_request(AUTH_SERVICE_URL, path)

@app.route('/user/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@limiter.limit("50 per minute")  # Límite moderado para usuarios
def user_proxy(path):
    """Proxy para el servicio de usuarios MongoDB"""
    return proxy_request(USER_SERVICE_URL, path)

# ===========================================
# ========= PROXY PARA TASK SERVICE ========
# ===========================================

# Endpoints de autenticación del Task Service
@app.route('/login', methods=['POST'])
def login_proxy():
    """Proxy directo para login del Auth Service MongoDB"""
    return proxy_request(AUTH_SERVICE_URL, 'login')

@app.route('/register', methods=['POST'])
def register_proxy():
    """Proxy directo para registro del Auth Service MongoDB"""
    return proxy_request(AUTH_SERVICE_URL, 'register')

# Endpoints principales de tareas
@app.route('/tasks', methods=['GET'])
def get_tasks_proxy():
    """Proxy para obtener todas las tareas del Task Service MongoDB"""
    return proxy_request(TASK_SERVICE_URL, 'tasks')

@app.route('/task', methods=['POST'])
def create_task_proxy():
    """Proxy para crear una nueva tarea en el Task Service MongoDB"""
    return proxy_request(TASK_SERVICE_URL, 'task')

@app.route('/task/<task_id>', methods=['GET', 'PUT', 'DELETE'])
@limiter.limit("50 per minute")  # Límite moderado para tareas
def task_proxy(task_id):
    """Proxy para operaciones específicas de tarea en el Task Service MongoDB"""
    return proxy_request(TASK_SERVICE_URL, f'task/{task_id}')

# Endpoints adicionales de tareas
@app.route('/tasks/status/<status>', methods=['GET'])
def tasks_by_status_proxy(status):
    """Proxy para obtener tareas por status del Task Service MongoDB"""
    return proxy_request(TASK_SERVICE_URL, f'tasks/status/{status}')

# Endpoint de información del sistema
@app.route('/info', methods=['GET'])
def info_proxy():
    """Proxy para información del sistema del Task Service MongoDB"""
    return proxy_request(TASK_SERVICE_URL, 'info')

@app.route('/health', methods=['GET'])
@limiter.limit("200 per minute")  # Health check más permisivo
def health_check():
    """Health check endpoint para Render"""
    try:
        # Probar conexión a MongoDB Atlas
        try:
            from database_mongo_render import mongo_db
            mongo_connected = mongo_db.connect()
        except ImportError:
            # Fallback a la configuración local si no está disponible
            from database_mongo import mongo_db
            mongo_connected = mongo_db.connect()
        
        # Verificar que las colecciones principales existan
        collections_status = {}
        if mongo_connected:
            try:
                db = mongo_db.db  # Usar el atributo db directamente
                collections = ['users', 'tasks', 'roles']
                for collection in collections:
                    try:
                        # Intentar contar documentos para verificar que la colección funciona
                        count = db[collection].count_documents({})
                        collections_status[collection] = f"OK ({count} docs)"
                    except Exception as e:
                        collections_status[collection] = f"Error: {str(e)}"
            except Exception as e:
                collections_status = {"error": f"Error accediendo a la base de datos: {str(e)}"}
        else:
            collections_status = {"error": "No se pudo conectar a MongoDB Atlas"}
        
        # Verificar archivo de logs
        logs_status = "OK"
        if not os.path.exists(LOG_FILE):
            logs_status = "Archivo de logs no encontrado"
        else:
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    log_lines = len(f.readlines())
                logs_status = f"OK ({log_lines} líneas)"
            except Exception as e:
                logs_status = f"Error leyendo logs: {str(e)}"
        
        # Verificar variables de entorno críticas
        env_status = {
            "MONGO_URI_ATLAS": "Configurada" if os.getenv('MONGO_URI_ATLAS') else "No configurada",
            "JWT_SECRET_ATLAS": "Configurado" if os.getenv('JWT_SECRET_ATLAS') else "No configurado",
            "FLASK_ENV": os.getenv('FLASK_ENV', 'No configurado')
        }
        
        return jsonify({
            'status': 'healthy' if mongo_connected else 'unhealthy',
            'message': 'Todos los servicios funcionando' if mongo_connected else 'Problemas de conectividad',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'API Gateway (MongoDB)',
            'mongodb': 'connected' if mongo_connected else 'disconnected',
            'collections': collections_status,
            'logs': logs_status,
            'environment': env_status,
            'render_ready': True
        }), 200 if mongo_connected else 503
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'render_ready': False
        }), 500

@app.route('/logs/stats', methods=['GET'])
@limiter.limit("50 per minute")  # Límite moderado para estadísticas
def get_logs_stats():
    """Endpoint para obtener estadísticas de logs para las gráficas"""
    try:
        # Leer el archivo de logs
        if not os.path.exists(LOG_FILE):
            return jsonify({"error": "Archivo de logs no encontrado"}), 404
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Contadores para estadísticas
        stats = {
            'total_requests': 0,
            'requests_by_method': {'GET': 0, 'POST': 0, 'PUT': 0, 'DELETE': 0, 'OPTIONS': 0},
            'requests_by_service': {'auth_service_mongo': 0, 'user_service_mongo': 0, 'task_service_mongo': 0, 'api_gateway': 0},
            'requests_by_status': {'2xx': 0, '3xx': 0, '4xx': 0, '5xx': 0},
            'response_times': {'fast': 0, 'medium': 0, 'slow': 0},  # <100ms, 100-500ms, >500ms
            'top_users': {},
            'hourly_distribution': {str(i).zfill(2): 0 for i in range(24)},
            'average_response_time': 0,
            'success_rate': 0
        }
        
        total_response_time = 0
        successful_requests = 0
        
        # Procesar cada línea del log
        for line in lines:
            if 'REQUEST_START:' in line:
                try:
                    # Extraer datos del log
                    log_start = line.find('REQUEST_START:') + len('REQUEST_START:')
                    log_data = json.loads(line[log_start:])
                    
                    # Contar por método
                    method = log_data.get('method', 'UNKNOWN')
                    if method in stats['requests_by_method']:
                        stats['requests_by_method'][method] += 1
                    
                    # Contar por usuario
                    user = log_data.get('user', {})
                    if user and user.get('username'):
                        username = user['username']
                        stats['top_users'][username] = stats['top_users'].get(username, 0) + 1
                    
                    # Distribución por hora
                    timestamp = log_data.get('timestamp', '')
                    if timestamp:
                        try:
                            hour = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).hour
                            stats['hourly_distribution'][str(hour).zfill(2)] += 1
                        except:
                            pass
                    
                    stats['total_requests'] += 1
                    
                except json.JSONDecodeError:
                    continue
            
            elif 'RESPONSE_END:' in line:
                try:
                    # Extraer datos del log
                    log_start = line.find('RESPONSE_END:') + len('RESPONSE_END:')
                    log_data = json.loads(line[log_start:])
                    
                    # Contar por servicio
                    service = log_data.get('service', 'unknown')
                    if service in stats['requests_by_service']:
                        stats['requests_by_service'][service] += 1
                    
                    # Contar por status code
                    status_code = log_data.get('status_code', 0)
                    if 200 <= status_code < 300:
                        stats['requests_by_status']['2xx'] += 1
                        successful_requests += 1
                    elif 300 <= status_code < 400:
                        stats['requests_by_status']['3xx'] += 1
                    elif 400 <= status_code < 500:
                        stats['requests_by_status']['4xx'] += 1
                    elif 500 <= status_code < 600:
                        stats['requests_by_status']['5xx'] += 1
                    
                    # Clasificar response time
                    response_time_ms = log_data.get('response_time_ms', 0)
                    total_response_time += response_time_ms
                    
                    if response_time_ms < 100:
                        stats['response_times']['fast'] += 1
                    elif response_time_ms < 500:
                        stats['response_times']['medium'] += 1
                    else:
                        stats['response_times']['slow'] += 1
                        
                except json.JSONDecodeError:
                    continue
        
        # Calcular estadísticas adicionales
        if stats['total_requests'] > 0:
            stats['average_response_time'] = round(total_response_time / stats['total_requests'], 2)
            stats['success_rate'] = round((successful_requests / stats['total_requests']) * 100, 1)
        
        # Ordenar usuarios por cantidad de peticiones
        stats['top_users'] = dict(sorted(stats['top_users'].items(), key=lambda x: x[1], reverse=True)[:10])
        
        return jsonify({
            "success": True,
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de logs: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint para Render"""
    try:
        # Verificar configuración
        print(f"🔍 [HEALTH] Verificando configuración...")
        print(f"   FLASK_ENV: {os.getenv('FLASK_ENV')}")
        print(f"   CORS Origins: {config.CORS_ORIGINS}")
        
        # Probar conexión a MongoDB
        try:
            from database_mongo_render import mongo_db
            connected = mongo_db.connect()
            mongodb_status = "connected" if connected else "disconnected"
        except Exception as e:
            mongodb_status = f"error: {str(e)}"
        
        return jsonify({
            'status': 'healthy',
            'message': 'API Gateway funcionando correctamente',
            'environment': os.getenv('FLASK_ENV', 'unknown'),
            'mongodb': mongodb_status,
            'cors_origins': config.CORS_ORIGINS,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ [HEALTH] Error en health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Endpoint raíz con información del API Gateway MongoDB"""
    return jsonify({
        "service": "API Gateway (MongoDB)",
        "version": "1.0.0",
        "description": "Gateway para microservicios de gestión de tareas con MongoDB",
        "database": "MongoDB",
        "endpoints": {
            "auth": "/auth/*",
            "users": "/user/*", 
            "tasks": "/task/*",
            "health": "/health",
            "logs": "/logs/stats"
        }
    })

if __name__ == '__main__':
    # Configuración para desarrollo local vs producción (Render)
    port = int(os.environ.get('PORT', config.API_GATEWAY_PORT))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print("=" * 50)
    print("INICIANDO API GATEWAY (MongoDB)")
    print("=" * 50)
    print(f"Gateway URL: http://localhost:{port}")
    print(f"Health Check: http://localhost:{port}/health")
    print(f"Environment: {'Production' if not debug_mode else 'Development'}")
    print("=" * 50)
    print("SERVICIOS MONGODB CONFIGURADOS:")
    print(f"   Auth Service:  {AUTH_SERVICE_URL}")
    print(f"   User Service:  {USER_SERVICE_URL}")
    print(f"   Task Service:  {TASK_SERVICE_URL}")
    print("=" * 50)
    print(f"CORS configurado para: {config.CORS_ORIGINS}")
    print("=" * 50)
    
    # En producción (Render), usar gunicorn
    if os.environ.get('PORT'):
        print("🚀 Modo producción detectado - Usar gunicorn")
        print("   Comando: gunicorn --bind 0.0.0.0:PORT api_gateway.app_mongo:app")
    else:
        print("🔧 Modo desarrollo - Usar Flask dev server")
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
