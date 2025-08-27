import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = 'task_management'
    
    # JWT Configuration
    JWT_SECRET = os.getenv('JWT_SECRET', 'tu_jwt_secret_super_seguro_para_desarrollo')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION = 24 * 60 * 60  # 24 horas
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Service Ports
    AUTH_SERVICE_PORT = int(os.getenv('AUTH_SERVICE_PORT', 5001))
    USER_SERVICE_PORT = int(os.getenv('USER_SERVICE_PORT', 5002))
    TASK_SERVICE_PORT = int(os.getenv('TASK_SERVICE_PORT', 5003))
    API_GATEWAY_PORT = int(os.getenv('API_GATEWAY_PORT', 4000))
    
    # CORS Configuration
    CORS_ORIGINS = [
        "https://microservicio-extraordinario.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ]

# Instancia global de configuración
config = Config()
