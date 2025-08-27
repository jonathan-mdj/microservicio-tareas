# config_production.py - Configuración para producción en Render
import os
from dotenv import load_dotenv

# Cargar variables de entorno para producción
load_dotenv('.env.atlas')

class ProductionConfig:
    """Configuración para producción en Render"""
    
    # MongoDB Atlas Configuration
    MONGO_URI = os.getenv('MONGO_URI_ATLAS', '')
    MONGO_DB_NAME = 'task_management'
    
    # JWT Configuration
    JWT_SECRET = os.getenv('JWT_SECRET_ATLAS', '')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION = 24 * 60 * 60  # 24 horas
    
    # Environment Configuration
    FLASK_ENV = 'production'
    DEBUG = False
    
    # Service Ports para Render
    PORT = int(os.environ.get('PORT', 10000))  # Render usa PORT
    AUTH_SERVICE_PORT = 5001
    USER_SERVICE_PORT = 5002
    TASK_SERVICE_PORT = 5003
    
    # CORS Origins para producción
    CORS_ORIGINS = [
        "https://microservicio-extraordinario.vercel.app",
        "https://microservicio-extraordinario-*.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    
    # MongoDB Atlas specific settings
    ATLAS_CLUSTER_NAME = os.getenv('ATLAS_CLUSTER_NAME', 'containerjonathan')
    ATLAS_USERNAME = os.getenv('ATLAS_USERNAME', 'microservicio-user')
    ATLAS_PASSWORD = os.getenv('ATLAS_PASSWORD', '')
    ATLAS_DATABASE = 'task_management'
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/api_gateway_production.log'
    
    # Rate Limiting para producción
    RATE_LIMIT_DEFAULT = "100 per minute"
    RATE_LIMIT_AUTH = "30 per minute"
    RATE_LIMIT_TASKS = "50 per minute"
    
    @classmethod
    def get_atlas_uri(cls):
        """Generar URI de MongoDB Atlas"""
        if cls.MONGO_URI:
            return cls.MONGO_URI
        
        if cls.ATLAS_USERNAME and cls.ATLAS_PASSWORD:
            return f"mongodb+srv://{cls.ATLAS_USERNAME}:{cls.ATLAS_PASSWORD}@{cls.ATLAS_CLUSTER_NAME}.fhwuyhh.mongodb.net/?retryWrites=true&w=majority"
        
        return None
    
    @classmethod
    def validate_config(cls):
        """Validar que la configuración de producción esté completa"""
        errors = []
        
        if not cls.get_atlas_uri():
            errors.append("MONGO_URI_ATLAS no configurada")
        
        if not cls.ATLAS_PASSWORD:
            errors.append("ATLAS_PASSWORD no configurada")
        
        if not cls.JWT_SECRET:
            errors.append("JWT_SECRET_ATLAS no configurado")
        
        if cls.JWT_SECRET == 'tu_jwt_secret_super_seguro_para_produccion_cambiar_esto':
            errors.append("JWT_SECRET_ATLAS debe ser cambiado en producción")
        
        return errors
    
    @classmethod
    def get_service_urls(cls):
        """Obtener URLs de servicios para producción"""
        base_url = f"http://localhost:{cls.PORT}"
        return {
            'auth_service': f"http://localhost:{cls.AUTH_SERVICE_PORT}",
            'user_service': f"http://localhost:{cls.USER_SERVICE_PORT}",
            'task_service': f"http://localhost:{cls.TASK_SERVICE_PORT}",
            'api_gateway': base_url
        }

# Instancia de configuración de producción
production_config = ProductionConfig()

if __name__ == "__main__":
    print("🔧 Configuración de Producción para Render:")
    print(f"   Port: {production_config.PORT}")
    print(f"   Environment: {production_config.FLASK_ENV}")
    print(f"   Debug: {production_config.DEBUG}")
    print(f"   MongoDB: {'CONFIGURADO' if production_config.get_atlas_uri() else 'NO CONFIGURADO'}")
    print(f"   JWT Secret: {'CONFIGURADO' if production_config.JWT_SECRET else 'NO CONFIGURADO'}")
    
    # Validar configuración
    errors = production_config.validate_config()
    if errors:
        print("\n❌ Errores de configuración:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("\n✅ Configuración de producción válida")
        print("🚀 Listo para despliegue en Render")
