# 📊 Sistema de Logs - API Gateway

## 🎯 Descripción

Sistema completo de logging implementado en el API Gateway que registra todas las peticiones y respuestas de los microservicios del sistema de gestión de tareas.

## ✨ Características Implementadas

### ✅ Factores Evaluados (Requerimientos)

- **📊 Response Time**: Tiempo de respuesta en milisegundos y segundos
- **🔧 Servicio API**: Identificación del microservicio (auth_service, user_service, task_service, api_gateway)
- **⏰ Timestamp**: Marca de tiempo ISO 8601 completa
- **📋 Status Code**: Código de estado HTTP de la respuesta
- **👤 Usuario**: Información del usuario extraída del token JWT

### 🚀 Características Adicionales

- **🔄 Rotación automática** de archivos de log (10MB máximo, 5 archivos de backup)
- **📈 Niveles de log** (INFO, WARNING, ERROR) basados en códigos de estado
- **🔍 Tracking completo** de peticiones y respuestas
- **📱 Información detallada** (IP, User-Agent, Content-Length)
- **🎨 Formato JSON** estructurado para fácil parsing

## 📁 Estructura de Archivos

```
Backend/api_gateway/
├── app.py                 # API Gateway con sistema de logs
├── log_viewer.py         # Script para analizar logs
├── log_monitor.py        # Script para monitoreo en tiempo real
├── logs/                 # Directorio de logs
│   ├── api_gateway.log   # Archivo principal de logs
│   ├── api_gateway.log.1 # Backup 1
│   ├── api_gateway.log.2 # Backup 2
│   └── ...
└── README_LOGS.md        # Esta documentación
```

## 🔧 Configuración

### Variables de Configuración

```python
# En app.py
LOG_DIR = 'logs'                    # Directorio de logs
LOG_FILE = 'logs/api_gateway.log'   # Archivo de log principal
JWT_SECRET = 'tu_clave_secreta_jwt_aqui'  # Clave para decodificar JWT
```

### Rotación de Logs

- **Tamaño máximo**: 10MB por archivo
- **Archivos de backup**: 5 archivos
- **Compresión**: Automática

## 📊 Formato de Logs

### Estructura de Log de Petición (REQUEST_START)

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "method": "POST",
  "endpoint": "login_proxy",
  "path": "/login",
  "url": "http://localhost:4000/login",
  "user_agent": "Mozilla/5.0...",
  "ip_address": "127.0.0.1",
  "user": {
    "user_id": 82,
    "username": "senior",
    "role_id": 1
  }
}
```

### Estructura de Log de Respuesta (RESPONSE_END)

```json
{
  "timestamp": "2024-01-15T10:30:45.456789",
  "method": "POST",
  "endpoint": "login_proxy",
  "path": "/login",
  "service": "task_service",
  "status_code": 200,
  "response_time_ms": 245.67,
  "response_time_seconds": 0.246,
  "content_length": 1024
}
```

## 🛠️ Herramientas de Análisis

### 1. Log Viewer (`log_viewer.py`)

Script para analizar y generar estadísticas de logs.

#### Uso Básico

```bash
# Ver logs de las últimas 24 horas
python log_viewer.py

# Ver logs de las últimas 48 horas
python log_viewer.py --hours 48

# Ver solo los últimos 20 logs
python log_viewer.py --recent 20

# Ver solo errores
python log_viewer.py --errors

# Ver solo estadísticas
python log_viewer.py --stats
```

#### Ejemplo de Salida

```
📊 ESTADÍSTICAS DE LOGS DEL API GATEWAY
============================================================

📈 RESUMEN GENERAL:
   Total de requests: 150
   Tiempo promedio de respuesta: 245.67ms
   Tiempo máximo de respuesta: 1250.45ms
   Tiempo mínimo de respuesta: 45.23ms

🔧 REQUESTS POR SERVICIO:
   task_service: 85 (56.7%)
   auth_service: 35 (23.3%)
   user_service: 20 (13.3%)
   api_gateway: 10 (6.7%)

🌐 REQUESTS POR MÉTODO HTTP:
   GET: 80 (53.3%)
   POST: 45 (30.0%)
   PUT: 15 (10.0%)
   DELETE: 10 (6.7%)

📋 CÓDIGOS DE ESTADO:
   ✅ 200: 140 (93.3%)
   ⚠️ 404: 5 (3.3%)
   ❌ 500: 5 (3.3%)

👥 USUARIOS MÁS ACTIVOS:
   senior: 45 requests
   admin: 30 requests
   user1: 25 requests
```

### 2. Log Monitor (`log_monitor.py`)

Script para monitorear logs en tiempo real.

#### Uso Básico

```bash
# Monitorear en tiempo real (formato mejorado)
python log_monitor.py

# Ver solo las últimas 20 líneas sin seguir
python log_monitor.py --lines 20 --no-follow

# Monitorear en formato raw
python log_monitor.py --raw
```

#### Ejemplo de Salida

```
14:30:45 📤 REQUEST POST    /login                          | Service: task_service | User: anonymous
14:30:45 📥 RESPONSE ✅ POST    /login                          | Service: task_service | Status: 200 | Time: 245.67ms | User: senior
14:30:46 📤 REQUEST GET     /tasks                          | Service: task_service | User: senior
14:30:46 📥 RESPONSE ✅ GET     /tasks                          | Service: task_service | Status: 200 | Time: 156.23ms | User: senior
```

## 📈 Métricas Capturadas

### Tiempo de Respuesta
- **Milisegundos**: Precisión de 2 decimales
- **Segundos**: Precisión de 3 decimales
- **Rango**: 0.001ms - 30 segundos (timeout)

### Servicios Identificados
- `auth_service`: Servicio de autenticación
- `user_service`: Servicio de usuarios
- `task_service`: Servicio de tareas
- `api_gateway`: Endpoints del gateway

### Códigos de Estado
- **2xx**: Éxito (INFO)
- **4xx**: Error del cliente (WARNING)
- **5xx**: Error del servidor (ERROR)

### Información del Usuario
- **user_id**: ID único del usuario
- **username**: Nombre de usuario
- **role_id**: ID del rol (1=admin, 2=user, 3=manager)
- **anonymous**: Para peticiones sin autenticación

## 🔍 Comandos Útiles

### Ver logs en tiempo real (Linux/Mac)
```bash
tail -f logs/api_gateway.log
```

### Buscar errores específicos
```bash
grep "ERROR" logs/api_gateway.log
grep "status_code.*5" logs/api_gateway.log
```

### Contar requests por servicio
```bash
grep "task_service" logs/api_gateway.log | wc -l
```

### Ver logs de un usuario específico
```bash
grep "senior" logs/api_gateway.log
```

## 🚨 Monitoreo de Errores

### Errores Comunes Detectados

1. **503 Service Unavailable**: Servicio no disponible
2. **504 Gateway Timeout**: Timeout del servicio
3. **500 Internal Server Error**: Error interno del servidor
4. **404 Not Found**: Endpoint no encontrado
5. **401 Unauthorized**: Token inválido o expirado

### Alertas Automáticas

El sistema registra automáticamente:
- **WARNING**: Para códigos 4xx
- **ERROR**: Para códigos 5xx
- **INFO**: Para códigos 2xx y 3xx

## 📊 Dashboard de Logs

Para crear un dashboard visual, puedes usar herramientas como:

- **Grafana**: Para visualización en tiempo real
- **ELK Stack**: Para análisis avanzado
- **Prometheus**: Para métricas de rendimiento
- **Kibana**: Para búsqueda y análisis

## 🔧 Configuración Avanzada

### Cambiar Nivel de Log

```python
# En app.py, función setup_logger()
logger.setLevel(logging.DEBUG)  # Para más detalle
logger.setLevel(logging.WARNING)  # Solo warnings y errores
```

### Cambiar Tamaño de Rotación

```python
# En app.py, función setup_logger()
file_handler = RotatingFileHandler(
    LOG_FILE, 
    maxBytes=50*1024*1024,  # 50MB
    backupCount=10          # 10 archivos de backup
)
```

### Agregar Logs Personalizados

```python
# En cualquier función
logger.info("Mensaje personalizado")
logger.warning("Advertencia personalizada")
logger.error("Error personalizado")
```

## 🎯 Beneficios del Sistema

1. **📊 Visibilidad completa** de todas las peticiones
2. **🔍 Debugging rápido** de problemas
3. **📈 Análisis de rendimiento** en tiempo real
4. **👥 Tracking de usuarios** para auditoría
5. **🚨 Detección temprana** de errores
6. **📋 Cumplimiento** de requisitos de logging

## 🔐 Seguridad

- **No se registran** contraseñas ni datos sensibles
- **Tokens JWT** se decodifican solo para extraer información básica
- **IPs y User-Agents** se registran para auditoría
- **Rotación automática** previene archivos muy grandes

---

**🎉 Sistema de Logs implementado exitosamente en el API Gateway!** 