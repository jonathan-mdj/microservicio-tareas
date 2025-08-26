# config_atlas.py - Configuración para MongoDB Atlas
import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env.atlas
load_dotenv('.env.atlas')

class AtlasConfig:
    # MongoDB Atlas Configuration
    MONGO_URI = os.getenv('MONGO_URI_ATLAS', '')
    MONGO_DB_NAME = 'task_management'
    
    # JWT Configuration
    JWT_SECRET = os.getenv('JWT_SECRET_ATLAS', 'tu_jwt_secret_super_seguro_para_produccion')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION = 24 * 60 * 60  # 24 horas
    
    # Environment Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Service Ports (para desarrollo local con Atlas)
    AUTH_SERVICE_PORT = int(os.getenv('AUTH_SERVICE_PORT', 5001))
    USER_SERVICE_PORT = int(os.getenv('USER_SERVICE_PORT', 5002))
    TASK_SERVICE_PORT = int(os.getenv('TASK_SERVICE_PORT', 5003))
    API_GATEWAY_PORT = int(os.getenv('API_GATEWAY_PORT', 4000))
    
    # CORS Origins para producción
    CORS_ORIGINS = [
        'http://localhost:4200',  # Desarrollo local
        'https://tu-frontend-vercel.vercel.app',  # Frontend en Vercel
        'https://tu-dominio.com'  # Tu dominio personalizado si lo tienes
    ]
    
    # MongoDB Atlas specific settings
    ATLAS_CLUSTER_NAME = os.getenv('ATLAS_CLUSTER_NAME', 'containerjonathan')
    ATLAS_USERNAME = os.getenv('ATLAS_USERNAME', 'microservicio-user')
    ATLAS_PASSWORD = os.getenv('ATLAS_PASSWORD', '')
    ATLAS_DATABASE = 'task_management'
    
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
        """Validar que la configuración esté completa"""
        errors = []
        
        if not cls.get_atlas_uri():
            errors.append("MONGO_URI_ATLAS o credenciales de Atlas no configuradas")
        
        if not cls.ATLAS_PASSWORD:
            errors.append("ATLAS_PASSWORD no configurada")
        
        if cls.JWT_SECRET == 'tu_jwt_secret_super_seguro_para_produccion':
            errors.append("JWT_SECRET_ATLAS debe ser cambiado en producción")
        
        return errors

# Instancia de configuración
atlas_config = AtlasConfig()

if __name__ == "__main__":
    print("🔧 Configuración de MongoDB Atlas:")
    print(f"   Cluster: {atlas_config.ATLAS_CLUSTER_NAME}")
    print(f"   Database: {atlas_config.ATLAS_DATABASE}")
    print(f"   Username: {atlas_config.ATLAS_USERNAME}")
    print(f"   Password: {'***' if atlas_config.ATLAS_PASSWORD else 'NO CONFIGURADA'}")
    print(f"   URI: {'CONFIGURADA' if atlas_config.get_atlas_uri() else 'NO CONFIGURADA'}")
    print(f"   JWT Secret: {'CONFIGURADO' if atlas_config.JWT_SECRET != 'tu_jwt_secret_super_seguro_para_produccion' else 'NO CONFIGURADO'}")
    
    # Validar configuración
    errors = atlas_config.validate_config()
    if errors:
        print("\n❌ Errores de configuración:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("\n✅ Configuración válida")
