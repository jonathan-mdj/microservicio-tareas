# 🛡️ Sistema de Rate Limiting - API Gateway

## 📋 Descripción

Sistema de protección contra ataques implementado en el API Gateway usando Flask-Limiter. Protege contra ataques de fuerza bruta, DDoS y abuso de la API.

## 🚀 Características

### **Protección por Endpoint**
- **Autenticación**: Límites estrictos para prevenir ataques de fuerza bruta
- **Usuarios**: Límites moderados para operaciones CRUD
- **Tareas**: Límites moderados para gestión de tareas
- **Sistema**: Límites permisivos para monitoreo

### **Límites Configurados**

#### **🔐 Autenticación (Más Estricto)**
- **Login**: 5 intentos por minuto
- **Registro**: 3 por hora
- **General**: 30 por minuto

#### **👥 Usuarios (Moderado)**
- **Lectura**: 100 por minuto
- **Escritura**: 20 por minuto
- **Eliminación**: 10 por minuto
- **General**: 50 por minuto

#### **📝 Tareas (Moderado)**
- **Lectura**: 100 por minuto
- **Escritura**: 30 por minuto
- **Eliminación**: 15 por minuto
- **General**: 50 por minuto

#### **⚙️ Sistema (Permisivo)**
- **Health Check**: 200 por minuto
- **Información**: 100 por minuto
- **General**: 100 por minuto

## 🛠️ Implementación

### **Archivos Principales**
- `app.py` - Implementación principal del rate limiting
- `rate_limiting.py` - Configuración y constantes
- `README_RATE_LIMITING.md` - Esta documentación

### **Dependencias**
```bash
pip install Flask-Limiter==3.5.0
```

### **Configuración Básica**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute", "1000 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)
```

## 📊 Headers de Respuesta

El sistema incluye headers informativos:

- `X-RateLimit-Limit`: Límite actual
- `X-RateLimit-Remaining`: Peticiones restantes
- `X-RateLimit-Reset`: Tiempo de reset
- `Retry-After`: Tiempo de espera recomendado

## 🚨 Manejo de Errores

### **Error 429 - Too Many Requests**
```json
{
  "error": "Rate limit exceeded",
  "message": "Demasiadas peticiones. Intenta de nuevo más tarde.",
  "retry_after": "60"
}
```

## 🔧 Configuración Avanzada

### **Almacenamiento**
- **Desarrollo**: Memoria (`memory://`)
- **Producción**: Redis (`redis://localhost:6379`)

### **Estrategias**
- **Fixed Window**: Ventana fija de tiempo
- **Sliding Window**: Ventana deslizante (más preciso)

### **IPs Especiales**
- **Whitelist**: IPs permitidas sin límites
- **Blacklist**: IPs bloqueadas permanentemente

## 📈 Monitoreo

### **Logs Generados**
- Límites excedidos
- IPs bloqueadas
- Actividad sospechosa

### **Métricas Disponibles**
- Peticiones por IP
- Límites alcanzados
- Tiempo de respuesta

## 🚀 Uso en Producción

### **Recomendaciones**
1. **Redis**: Usar Redis para almacenamiento distribuido
2. **Monitoreo**: Implementar alertas para límites excedidos
3. **Ajuste**: Ajustar límites según el tráfico real
4. **Backup**: Configurar fallback a memoria si Redis falla

### **Escalabilidad**
- **Horizontal**: Múltiples instancias del gateway
- **Vertical**: Aumentar límites según recursos
- **Adaptativo**: Límites dinámicos según carga

## 🔒 Seguridad

### **Protecciones Implementadas**
- ✅ **Rate Limiting**: Previene abuso de la API
- ✅ **IP Filtering**: Control de IPs permitidas/bloqueadas
- ✅ **Method Filtering**: Límites diferentes por tipo de operación
- ✅ **Error Handling**: Respuestas seguras sin información sensible

### **Vectores de Ataque Mitigados**
- 🚫 **Fuerza Bruta**: Límites estrictos en autenticación
- 🚫 **DDoS**: Límites por IP y por endpoint
- 🚫 **Scraping**: Límites en operaciones de lectura
- 🚫 **Spam**: Límites en operaciones de escritura

## 📝 Ejemplos de Uso

### **Decorador Básico**
```python
@app.route('/api/endpoint')
@limiter.limit("10 per minute")
def endpoint():
    return jsonify({"message": "OK"})
```

### **Decorador Condicional**
```python
@app.route('/api/endpoint')
@limiter.limit("100 per minute")
def endpoint():
    if request.method == 'POST':
        # Límite más estricto para POST
        limiter.limit("20 per minute")(lambda: None)()
    return jsonify({"message": "OK"})
```

## 🔄 Actualizaciones

### **Versión 1.0.0**
- ✅ Implementación básica de rate limiting
- ✅ Límites por endpoint y método
- ✅ Manejo de errores 429
- ✅ Headers informativos

### **Próximas Versiones**
- 🔄 Límites dinámicos
- 🔄 Machine Learning para detección de anomalías
- 🔄 Dashboard de monitoreo
- 🔄 API para gestión de límites

---

**⚠️ Importante**: Este sistema es la primera línea de defensa. Debe complementarse con autenticación, autorización y validación de datos.
