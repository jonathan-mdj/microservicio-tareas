# user_service/app.py
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import bcrypt
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)



# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'auth_plugin': os.getenv('DB_AUTH_PLUGIN')
}

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

def convert_datetime_to_string(obj):
    """Convertir datetime a string de forma segura"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj) if obj is not None else None

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

@app.route('/users', methods=['GET', 'OPTIONS'])
def get_users():
    """Obtener lista de todos los usuarios"""
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
        
        # Convertir a lista de diccionarios mutables y procesar fechas
        processed_users = []
        for user in users:
            # Convertir a diccionario mutable de forma segura
            user_dict = {}
            for key, value in user.items():
                if key == 'created_at' and value:
                    user_dict[key] = convert_datetime_to_string(value)
                else:
                    user_dict[key] = value
            
            # No devolver información sensible
            if 'password' in user_dict:
                del user_dict['password']
            processed_users.append(user_dict)
        
        return jsonify({"users": processed_users, "count": len(processed_users)}), 200
        
    except Error as e:
        print(f"Error obteniendo usuarios: {e}")
        return jsonify({"error": "Error obteniendo usuarios"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/users/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_user(user_id):
    """Obtener un usuario específico por ID"""
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
            WHERE u.id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Convertir a diccionario mutable y procesar fecha
        user_dict = {}
        for key, value in user.items():
            if key == 'created_at' and value:
                user_dict[key] = convert_datetime_to_string(value)
            else:
                user_dict[key] = value
        
        return jsonify({"user": user_dict}), 200
        
    except Error as e:
        print(f"Error obteniendo usuario: {e}")
        return jsonify({"error": "Error obteniendo usuario"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/users', methods=['POST', 'OPTIONS'])
def create_user():
    """Crear un nuevo usuario"""
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        # Validaciones de entrada
        if not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username y password requeridos"}), 400
        
        username = data['username'].strip()
        password = data['password']
        email = data.get('email', '').strip() if data.get('email') else None
        role_id = data.get('role_id', 2)  # 2 = user por defecto
        
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
        
        # Hashear contraseña
        hashed_pw = hash_password(password)
        
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        cursor = connection.cursor()
        try:
            # Verificar si el usuario ya existe
            if email:
                cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', 
                              (username, email))
            else:
                cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            
            existing_user = cursor.fetchone()
            
            if existing_user:
                return jsonify({"error": "El usuario o email ya existe"}), 400
            
            # Insertar nuevo usuario
            cursor.execute(
                'INSERT INTO users (username, password, email, role_id) VALUES (%s, %s, %s, %s)',
                (username, hashed_pw, email, role_id)
            )
            connection.commit()
            
            user_id = cursor.lastrowid
            
            # Obtener información del usuario creado
            cursor.execute("""
                SELECT u.id, u.username, u.email, u.created_at, r.nombre as role
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                WHERE u.id = %s
            """, (user_id,))
            
            new_user = cursor.fetchone()
            
            if new_user and new_user[3]:  # created_at está en posición 3
                user_data = {
                    "id": new_user[0],
                    "username": new_user[1],
                    "email": new_user[2],
                    "created_at": convert_datetime_to_string(new_user[3]),
                    "role": new_user[4]
                }
            else:
                user_data = {
                    "id": user_id,
                    "username": username,
                    "email": email,
                    "role_id": role_id
                }
            
            return jsonify({
                "message": "Usuario creado exitosamente",
                "user": user_data
            }), 201
            
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
            print(f"Error creando usuario: {e}")
            return jsonify({"error": "Error creando usuario"}), 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        print(f"Error general creando usuario: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/users/<int:user_id>', methods=['PUT', 'OPTIONS'])
def update_user(user_id):
    """Actualizar un usuario existente"""
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        cursor = connection.cursor()
        try:
            # Verificar si el usuario existe
            cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Usuario no encontrado"}), 404
            
            # Preparar campos para actualizar
            update_fields = []
            values = []
            
            if 'username' in data and data['username'].strip():
                update_fields.append('username = %s')
                values.append(data['username'].strip())
            
            if 'email' in data:
                email = data['email'].strip() if data['email'] else None
                if email:
                    import re
                    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                    if not re.match(email_pattern, email):
                        return jsonify({"error": "El email no tiene un formato válido"}), 400
                update_fields.append('email = %s')
                values.append(email)
            
            if 'password' in data and data['password']:
                if len(data['password']) < 6:
                    return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
                hashed_pw = hash_password(data['password'])
                update_fields.append('password = %s')
                values.append(hashed_pw)
            
            if 'role_id' in data:
                update_fields.append('role_id = %s')
                values.append(data['role_id'])
            
            if not update_fields:
                return jsonify({"error": "No hay campos para actualizar"}), 400
            
            # Ejecutar actualización
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(query, values)
            connection.commit()
            
            # Obtener usuario actualizado
            cursor.execute("""
                SELECT u.id, u.username, u.email, u.created_at, r.nombre as role
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                WHERE u.id = %s
            """, (user_id,))
            
            updated_user = cursor.fetchone()
            
            if updated_user:
                user_data = {
                    "id": updated_user[0],
                    "username": updated_user[1],
                    "email": updated_user[2],
                    "created_at": convert_datetime_to_string(updated_user[3]),
                    "role": updated_user[4]
                }
            else:
                user_data = {"id": user_id}
            
            return jsonify({
                "message": "Usuario actualizado exitosamente",
                "user": user_data
            }), 200
            
        except mysql.connector.IntegrityError as e:
            connection.rollback()
            error_msg = str(e).lower()
            if "username" in error_msg:
                return jsonify({"error": "El nombre de usuario ya existe"}), 400
            elif "email" in error_msg:
                return jsonify({"error": "El email ya está registrado"}), 400
            else:
                return jsonify({"error": "Conflicto de datos"}), 400
        except Error as e:
            connection.rollback()
            print(f"Error actualizando usuario: {e}")
            return jsonify({"error": "Error actualizando usuario"}), 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        print(f"Error general actualizando usuario: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/users/<int:user_id>', methods=['DELETE', 'OPTIONS'])
def delete_user(user_id):
    """Eliminar un usuario (soft delete)"""
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    cursor = connection.cursor()
    try:
        # Verificar si el usuario existe
        cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # En lugar de eliminar, podríamos hacer soft delete
        # Por ahora, eliminamos directamente
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        connection.commit()
        
        return jsonify({"message": "Usuario eliminado exitosamente"}), 200
        
    except Error as e:
        connection.rollback()
        print(f"Error eliminando usuario: {e}")
        return jsonify({"error": "Error eliminando usuario"}), 500
    finally:
        cursor.close()
        connection.close()

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
        "service": "User Service",
        "database": db_status,
        "port": 5002
    }), 200

@app.route('/roles', methods=['GET', 'OPTIONS'])
def get_roles():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute('SELECT id, nombre FROM roles ORDER BY id')
        roles = cursor.fetchall()
        return jsonify({"roles": roles, "count": len(roles)})
    except Error as e:
        return jsonify({"error": f"Error obteniendo roles: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/', methods=['GET', 'OPTIONS'])
def root():
    """Información del servicio"""
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    return jsonify({
        "service": "User Service",
        "version": "1.0.0",
        "port": 5002,
        "endpoints": {
            "list_users": "GET /users",
            "get_user": "GET /users/{id}",
            "create_user": "POST /users",
            "update_user": "PUT /users/{id}",
            "delete_user": "DELETE /users/{id}",
            "get_roles": "GET /roles",
            "health": "GET /health"
        },
        "database": "MySQL task_management"
    }), 200

if __name__ == '__main__':
    print("=" * 50)
    print("INICIANDO USER SERVICE")
    print("=" * 50)
    print("User Service URL: http://localhost:5002")
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
    app.run(host='0.0.0.0', port=5002, debug=True)