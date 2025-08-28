# auth_service/app_mongo.py
from flask import Flask, jsonify, request
import bcrypt
import os
import pyotp
import qrcode
import io
import base64
import jwt
import datetime
import traceback
from database_mongo import mongo_db
# Importar configuración según el entorno
import os
if os.getenv('FLASK_ENV') == 'production':
    from config_production import production_config as config
    print("🚀 [AUTH] Usando configuración de PRODUCCIÓN")
else:
    from config import config
    print("🔧 [AUTH] Usando configuración de DESARROLLO")

app = Flask(__name__)



print(f"[DB] Conectando a MongoDB: {config.MONGO_URI}")

def hash_password(password):
    """Hashear contraseña usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, user_password):
    """Verificar contraseña hasheada"""
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

# CORS manejado por API Gateway - no configurar aquí

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """Registrar nuevo usuario en MongoDB"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    try:
        data = request.get_json()
        print(f"[REGISTER] Datos recibidos: {data}")
        if not data:
            print("[REGISTER] No se recibieron datos")
            return jsonify({"error": "No se recibieron datos"}), 400
            
        # Validaciones de entrada
        if not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username y password requeridos"}), 400
        
        # Limpiar datos de entrada
        username = data['username'].strip()
        password = data['password']
        email = data.get('email', '').strip() if data.get('email') else None
        
        # Validaciones adicionales
        if len(username) < 3:
            return jsonify({"error": "El username debe tener al menos 3 caracteres"}), 400
            
        if len(password) < 6:
            return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
        
        # Conectar a MongoDB
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        users_collection = mongo_db.get_collection('users')
        
        # Verificar si el usuario ya existe
        existing_user = users_collection.find_one({
            "$or": [
                {"username": username},
                {"email": email} if email else {"username": "nonexistent"}
            ]
        })
        
        if existing_user:
            return jsonify({"error": "El usuario ya existe"}), 400
        
        # Hash de la contraseña
        hashed_password = hash_password(password)
        
        # Generar OTP secret
        otp_secret = pyotp.random_base32()
        
        # Generar QR code para OTP
        totp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(
            name=email if email else username,
            issuer_name="Task Management System"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir QR a base64
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_code_url = base64.b64encode(buffer.getvalue()).decode()
        
        # Crear documento de usuario
        user_doc = {
            "username": username,
            "email": email,
            "password": hashed_password.decode('utf-8'),
            "otp_secret": otp_secret,
            "role": "user",
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "require_otp": True
        }
        
        # Insertar usuario
        result = users_collection.insert_one(user_doc)
        
        print(f"[REGISTER] Usuario creado exitosamente: {username}")
        
        return jsonify({
            "message": "Usuario registrado exitosamente",
            "user_id": str(result.inserted_id),
            "otp_secret": otp_secret,
            "qr_code": qr_code_url
        }), 201
        
    except Exception as e:
        print(f"Error general en registro: {e}")
        print(f"Tipo de error: {type(e)}")
        print(f"Traceback completo:")
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Autenticar usuario desde MongoDB"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username y password requeridos"}), 400
        
        username = data.get('username').strip()
        password = data.get('password')
        otp_code = data.get('otp')
        
        # Conectar a MongoDB
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        users_collection = mongo_db.get_collection('users')
        
        # Verificar si es la cuenta Profesor por email (sin OTP)
        if username == 'prof@gmail.com':
            print(f"[LOGIN] Usuario Profesor detectado por email - omitiendo validación OTP")
            if not otp_code:
                # Para Profesor, el OTP es opcional
                otp_code = "000000"  # OTP dummy para mantener compatibilidad
            
            # Buscar usuario Profesor por email
            user = users_collection.find_one({"email": username})
            
            if user and check_password(user['password'], password):
                # Para Profesor, generar token sin verificar OTP
                payload = {
                    "user_id": str(user['_id']),
                    "username": user['username'],
                    "role": user['role'],
                    "sub": user['username'],
                    "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)
                }
                secret = config.JWT_SECRET
                token = jwt.encode(payload, secret, algorithm="HS256")
                
                response_data = {
                    "message": "Login exitoso (Profesor - sin OTP)",
                    "token": token,
                    "user": {
                        "id": str(user['_id']),
                        "username": user['username'],
                        "email": user['email'],
                        "role": user['role']
                    }
                }
                
                print(f"[LOGIN] Profesor autenticado exitosamente")
                return jsonify(response_data), 200
            else:
                print(f"[LOGIN] Credenciales inválidas para Profesor")
                return jsonify({"error": "Credenciales inválidas"}), 401
        else:
            # Para otros usuarios, verificar OTP normalmente
            if not otp_code:
                return jsonify({"error": "OTP requerido"}), 400
            
            # Buscar usuario por username o email
            user = users_collection.find_one({
                "$or": [
                    {"username": username},
                    {"email": username}
                ]
            })
            
            if user and check_password(user['password'], password):
                # Validar OTP
                otp_secret = user.get('otp_secret')
                if not otp_secret:
                    return jsonify({"error": "No se encontró el secreto OTP"}), 400
                
                totp = pyotp.TOTP(otp_secret)
                if not totp.verify(otp_code):
                    return jsonify({"error": "OTP inválido"}), 401
                
                # Generar JWT real con claim 'sub'
                payload = {
                    "user_id": str(user['_id']),
                    "username": user['username'],
                    "role": user['role'],
                    "sub": user['username'],
                    "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)
                }
                secret = config.JWT_SECRET
                token = jwt.encode(payload, secret, algorithm="HS256")
                
                response_data = {
                    "message": "Login exitoso",
                    "token": token,
                    "user": {
                        "id": str(user['_id']),
                        "username": user['username'],
                        "email": user['email'],
                        "role": user['role']
                    }
                }
                
                return jsonify(response_data), 200
            else:
                return jsonify({"error": "Credenciales inválidas"}), 401
            
    except Exception as e:
        print(f"Error general en login: {e}")
        print(f"Tipo de error: {type(e)}")
        print(f"Traceback completo:")
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    """Verificar estado del servicio"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    # Verificar conexión a MongoDB
    try:
        if mongo_db.connect():
            # Test connection
            mongo_db.client.admin.command('ismaster')
            db_status = "UP"
        else:
            db_status = "DOWN"
    except:
        db_status = "DOWN"
    
    # Este return debe estar FUERA del try/except
    return jsonify({
        "status": "UP" if db_status == "UP" else "DEGRADED",
        "service": "Auth Service (MongoDB)",
        "database": db_status,
        "port": os.environ.get('PORT', 'N/A')
    }), 200

@app.route('/', methods=['GET', 'OPTIONS'])
def root():
    """Información del servicio"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    return jsonify({
        "service": "Auth Service (MongoDB)",
        "version": "1.0.0",
        "port": os.environ.get('PORT', 'N/A'),
        "endpoints": {
            "register": "POST /auth/register",
            "login": "POST /auth/login",
            "health": "GET /health",
            "users": "GET /users"
        },
        "database": "MongoDB task_management"
    }), 200

@app.route('/users', methods=['GET', 'OPTIONS'])
def get_users():
    """Obtener lista de usuarios desde MongoDB"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    try:
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        users_collection = mongo_db.get_collection('users')
        
        # Obtener usuarios con roles
        users = list(users_collection.find({}, {
            "password": 0,  # Excluir password
            "otp_secret": 0  # Excluir OTP secret
        }))
        
        # Convertir ObjectId a string para JSON
        for user in users:
            user['_id'] = str(user['_id'])
            if user.get('created_at'):
                user['created_at'] = user['created_at'].isoformat()
        
        return jsonify({"users": users, "count": len(users)}), 200
        
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=config.DEBUG)
