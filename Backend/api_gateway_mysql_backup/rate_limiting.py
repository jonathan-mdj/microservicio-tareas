# api_gateway/rate_limiting.py
"""
Configuración de Rate Limiting para el API Gateway
Protege contra ataques de fuerza bruta y DDoS
"""

# Configuración de límites por tipo de operación
RATE_LIMITS = {
    # Autenticación - Límites estrictos para prevenir ataques
    'auth': {
        'login': "5 per minute",      # Máximo 5 intentos de login por minuto
        'register': "3 per hour",     # Máximo 3 registros por hora
        'default': "30 per minute"    # Límite general para auth
    },
    
    # Usuarios - Límites moderados
    'users': {
        'read': "100 per minute",     # Lecturas de usuarios
        'write': "20 per minute",     # Crear/actualizar usuarios
        'delete': "10 per minute",    # Eliminar usuarios
        'default': "50 per minute"    # Límite general para usuarios
    },
    
    # Tareas - Límites moderados
    'tasks': {
        'read': "100 per minute",     # Lecturas de tareas
        'write': "30 per minute",     # Crear/actualizar tareas
        'delete': "15 per minute",    # Eliminar tareas
        'default': "50 per minute"    # Límite general para tareas
    },
    
    # Sistema - Límites permisivos
    'system': {
        'health': "200 per minute",   # Health checks
        'info': "100 per minute",     # Información del sistema
        'default': "100 per minute"   # Límite general para sistema
    }
}

# Configuración de almacenamiento
STORAGE_CONFIG = {
    'type': 'memory',                 # Almacenamiento en memoria (para desarrollo)
    'uri': 'memory://',               # URI del almacenamiento
    'strategy': 'fixed-window'        # Estrategia de ventana fija
}

# Configuración de IPs permitidas (whitelist)
ALLOWED_IPS = [
    '127.0.0.1',      # Localhost
    '::1',            # IPv6 localhost
    'localhost'       # Nombre localhost
]

# Configuración de IPs bloqueadas (blacklist)
BLOCKED_IPS = [
    # Agregar IPs maliciosas aquí
]

# Configuración de headers de rate limiting
RATE_LIMIT_HEADERS = {
    'X-RateLimit-Limit': True,        # Mostrar límite actual
    'X-RateLimit-Remaining': True,    # Mostrar peticiones restantes
    'X-RateLimit-Reset': True,        # Mostrar tiempo de reset
    'Retry-After': True               # Mostrar tiempo de espera
}

# Configuración de logging
LOGGING_CONFIG = {
    'log_rate_limits': True,          # Log de límites excedidos
    'log_blocked_ips': True,          # Log de IPs bloqueadas
    'log_suspicious_activity': True   # Log de actividad sospechosa
}
