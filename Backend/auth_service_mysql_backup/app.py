# auth_service/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import bcrypt
import os
from dotenv import load_dotenv
import pyotp
import qrcode
import io
import base64
import jwt
import datetime

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)

# Configuración CORS
CORS(app, 
     origins=["http://localhost:4200", "http://localhost:4000"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=True,
     max_age=3600)

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'auth_plugin': os.getenv('DB_AUTH_PLUGIN')
}

print(f"[DB] Conectando a: {DB_CONFIG}")

def get_db_connection():
    """Obtener conexión a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def hash_password(password):
    """Hashear contraseña usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, user_password):
    """Verificar contraseña hasheada"""
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

# Manejo de preflight OPTIONS
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """Registrar nuevo usuario en la base de datos"""
    if request.method == 'OPTIONS':
        return handle_preflight()
    
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
        
        # Validar formato de email si se proporciona
        if email:
            import re
            email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_pattern, email):
                return jsonify({"error": "El email no tiene un formato válido"}), 400
        
        connection = get_db_connection()
        if not connection:
            print("[REGISTER] Error de conexión a la base de datos")
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        cursor = connection.cursor()
        try:
            # Verificar si el usuario ya existe
            print(f"[REGISTER] Verificando si existe usuario: username='{username}', email='{email}'")
            if email:
                cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', 
                              (username, email))
            else:
                cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            
            existing_user = cursor.fetchone()
            print(f"[REGISTER] Usuario existente: {existing_user}")
            
            if existing_user:
                print("[REGISTER] El usuario o email ya existe")
                return jsonify({"error": "El usuario o email ya existe"}), 400
            
            print(f"[REGISTER] Generando OTP secret...")
            # Generar secreto OTP
            otp_secret = pyotp.random_base32()
            print(f"[REGISTER] OTP secret generado: {otp_secret}")
            
            print(f"[REGISTER] Hasheando contraseña...")
            # Hashear contraseña
            hashed_pw = hash_password(password)
            print(f"[REGISTER] Contraseña hasheada correctamente")
            
            print(f"[REGISTER] Insertando usuario en la base de datos...")
            # Insertar nuevo usuario con otp_secret
            cursor.execute(
                'INSERT INTO users (username, password, email, role_id, otp_secret) VALUES (%s, %s, %s, %s, %s)',
                (username, hashed_pw, email, 2, otp_secret)
            )
            connection.commit()
            user_id = cursor.lastrowid
            print(f"[REGISTER] Usuario insertado con id: {user_id}")
            
            print(f"[REGISTER] Generando QR code...")
            # Generar URI y QR
            totp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(name=username, issuer_name="MicroServicioApp")
            print(f"[REGISTER] TOTP URI generado: {totp_uri}")
            
            qr = qrcode.make(totp_uri)
            print(f"[REGISTER] QR code generado")
            
            buf = io.BytesIO()
            qr.save(buf, format='PNG')
            qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            print(f"[REGISTER] QR code convertido a base64")
            
            cursor.execute("SELECT id, username, email FROM users ORDER BY id DESC LIMIT 5")
            print("[DB] Últimos usuarios:", cursor.fetchall())
            
            response_data = {
                "message": "Usuario registrado exitosamente",
                "user": {
                    "id": user_id,
                    "username": username,
                    "email": email
                },
                "otp_qr": qr_b64
            }
            
            print(f"[REGISTER] Respuesta preparada, enviando...")
            return jsonify(response_data), 201
            
        except mysql.connector.IntegrityError as e:
            connection.rollback()
            error_msg = str(e).lower()
            if "username" in error_msg:
                return jsonify({"error": "El nombre de usuario ya existe"}), 400
            elif "email" in error_msg:
                return jsonify({"error": "El email ya está registrado"}), 400
            else:
                return jsonify({"error": "El usuario ya existe"}), 400
        except Error as e:
            connection.rollback()
            print(f"Error en registro: {e}")
            print(f"Tipo de error: {type(e)}")
            print(f"Detalles del error: {str(e)}")
            return jsonify({"error": f"Error creando usuario: {str(e)}"}), 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        import traceback
        print(f"Error general en registro: {e}")
        print(f"Tipo de error: {type(e)}")
        print(f"Traceback completo:")
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Autenticar usuario desde la base de datos"""
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username y password requeridos"}), 400
        
        username = data.get('username').strip()
        password = data.get('password')
        otp_code = data.get('otp')
        
        # Verificar si es la cuenta Profesor por email (sin OTP)
        if username == 'prof@gmail.com':
            print(f"[LOGIN] Usuario Profesor detectado por email - omitiendo validación OTP")
            if not otp_code:
                # Para Profesor, el OTP es opcional
                otp_code = "000000"  # OTP dummy para mantener compatibilidad
            
            connection = get_db_connection()
            if not connection:
                return jsonify({"error": "Error de conexión a la base de datos"}), 500
            
            cursor = connection.cursor(dictionary=True)
            try:
                # Buscar usuario Profesor por email
                cursor.execute(
                    'SELECT * FROM users WHERE email = %s', 
                    (username,)
                )
                user = cursor.fetchone()
                
                if user and check_password(user['password'], password):
                    # Para Profesor, generar token sin verificar OTP
                    payload = {
                        "user_id": user['id'],
                        "username": user['username'],
                        "role_id": user['role_id'],
                        "sub": user['username'],
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
                    }
                    secret = os.getenv("JWT_SECRET", "supersecretkey")
                    token = jwt.encode(payload, secret, algorithm="HS256")
                    if isinstance(token, bytes):
                        token = token.decode('utf-8')
                    
                    response_data = {
                        "message": "Login exitoso (Profesor - sin OTP)",
                        "token": token,
                        "user": {
                            "id": user['id'],
                            "username": user['username'],
                            "email": user['email'],
                            "role_id": user['role_id']
                        }
                    }
                    
                    print(f"[LOGIN] Profesor autenticado exitosamente")
                    return jsonify(response_data), 200
                else:
                    print(f"[LOGIN] Credenciales inválidas para Profesor")
                    return jsonify({"error": "Credenciales inválidas"}), 401
                    
            except Error as e:
                print(f"Error en login Profesor: {e}")
                return jsonify({"error": "Error interno del servidor"}), 500
            finally:
                cursor.close()
                connection.close()
        else:
            # Para otros usuarios, verificar OTP normalmente
            if not otp_code:
                return jsonify({"error": "OTP requerido"}), 400
            
            connection = get_db_connection()
            if not connection:
                return jsonify({"error": "Error de conexión a la base de datos"}), 500
            
            cursor = connection.cursor(dictionary=True)
            try:
                # Buscar usuario por username o email
                cursor.execute(
                    'SELECT * FROM users WHERE username = %s OR email = %s', 
                    (username, username)
                )
                user = cursor.fetchone()
                
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
                        "user_id": user['id'],
                        "username": user['username'],
                        "role_id": user['role_id'],
                        "sub": user['username'],
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
                    }
                    secret = os.getenv("JWT_SECRET", "supersecretkey")
                    token = jwt.encode(payload, secret, algorithm="HS256")
                    if isinstance(token, bytes):
                        token = token.decode('utf-8')
                    
                    response_data = {
                        "message": "Login exitoso",
                        "token": token,
                        "user": {
                            "id": user['id'],
                            "username": user['username'],
                            "email": user['email'],
                            "role_id": user['role_id']
                        }
                    }
                    
                    return jsonify(response_data), 200
                else:
                    return jsonify({"error": "Credenciales inválidas"}), 401
                    
            except Error as e:
                print(f"Error en login: {e}")
                return jsonify({"error": "Error interno del servidor"}), 500
            finally:
                cursor.close()
                connection.close()
            
    except Exception as e:
        import traceback
        print(f"Error general en login: {e}")
        print(f"Tipo de error: {type(e)}")
        print(f"Traceback completo:")
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    """Verificar estado del servicio"""
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    # Verificar conexión a la base de datos
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            connection.close()
            db_status = "UP"
        except:
            db_status = "DOWN"
    else:
        db_status = "DOWN"
    
    return jsonify({
        "status": "UP" if db_status == "UP" else "DEGRADED",
        "service": "Auth Service",
        "database": db_status,
        "port": 5001
    }), 200

@app.route('/users', methods=['GET', 'OPTIONS'])
def get_users():
    """Obtener lista de usuarios (solo para admin)"""
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.created_at, r.nombre as role
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            ORDER BY u.created_at DESC
        """)
        users = cursor.fetchall()
        
        # Convertir datetime a string para JSON
        for user in users:
            if user['created_at']:
                user['created_at'] = user['created_at'].isoformat()
        
        return jsonify({"users": users, "count": len(users)}), 200
        
    except Error as e:
        print(f"Error obteniendo usuarios: {e}")
        return jsonify({"error": "Error obteniendo usuarios"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/', methods=['GET', 'OPTIONS'])
def root():
    """Información del servicio"""
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    return jsonify({
        "service": "Auth Service",
        "version": "1.0.0",
        "port": 5001,
        "endpoints": {
            "register": "POST /register",
            "login": "POST /login",
            "users": "GET /users",
            "health": "GET /health"
        },
        "database": "MySQL task_management"
    }), 200

if __name__ == '__main__':
    print("=" * 50)
    print("INICIANDO AUTH SERVICE")
    print("=" * 50)
    print("Auth Service URL: http://localhost:5001")
    print("Base de datos: MySQL task_management")
    print("CORS configurado para: http://localhost:4200, http://localhost:4000")
    print("=" * 50)
    
    # Verificar conexión a la base de datos al iniciar
    connection = get_db_connection()
    if connection:
        print("✓ Conexión a MySQL exitosa")
        connection.close()
    else:
        print("✗ Error conectando a MySQL")
        print("Verifica la configuración de la base de datos")
    
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)