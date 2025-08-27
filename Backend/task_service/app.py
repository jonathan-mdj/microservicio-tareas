# task_service/app.py
from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime
from auth import generate_token, token_required, hash_password, check_password
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'supersecretkey')



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
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def get_user_by_username(username):
    """Obtener usuario por username"""
    connection = get_db_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error obteniendo usuario: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def get_user_by_username_or_email(identifier):
    """Obtener usuario por username o email"""
    connection = get_db_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT * FROM users WHERE username = %s OR email = %s', 
            (identifier, identifier)
        )
        return cursor.fetchone()
    except Error as e:
        print(f"Error obteniendo usuario: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

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

# Rutas de autenticación
# @app.route('/login', methods=['POST', 'OPTIONS'])
# def login():
#     """Endpoint de login directo (DESACTIVADO: usar Auth Service)"""
#     if request.method == 'OPTIONS':
#         return handle_preflight()
        
#     try:
#         data = request.get_json()
#         if not data or not data.get('username') or not data.get('password'):
#             return jsonify({"error": "Username y contraseña requeridos"}), 400
        
#         user = get_user_by_username_or_email(data.get('username'))
        
#         if user and check_password(user['password'], data.get('password')):
#             token = generate_token(user['username'])
#             return jsonify({
#                 "token": token, 
#                 "message": "Login exitoso",
#                 "user": {
#                     "id": user['id'],
#                     "username": user['username'],
#                     "email": user['email'],
#                     "role_id": user['role_id']
#                 }
#             }), 200
#         return jsonify({"error": "Credenciales inválidas"}), 401
        
#     except Exception as e:
#         print(f"Error en login: {e}")
#         return jsonify({"error": "Error interno del servidor"}), 500

# @app.route('/register', methods=['POST', 'OPTIONS'])
# def register():
#     """Endpoint de registro directo (DESACTIVADO: usar Auth Service)"""
#     if request.method == 'OPTIONS':
#         return handle_preflight()
        
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "No se recibieron datos"}), 400
            
#         # Validaciones de entrada
#         if not data.get('username') or not data.get('password') or not data.get('email'):
#             return jsonify({"error": "Username, email y password requeridos"}), 400
        
#         # Limpiar datos de entrada
#         username = data['username'].strip()
#         email = data['email'].strip().lower()
#         password = data['password']
        
#         # Validaciones adicionales
#         if len(username) < 3:
#             return jsonify({"error": "El username debe tener al menos 3 caracteres"}), 400
            
#         if len(password) < 6:
#             return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
        
#         # Validar formato de email
#         import re
#         email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
#         if not re.match(email_pattern, email):
#             return jsonify({"error": "El email no tiene un formato válido"}), 400
        
#         hashed_pw = hash_password(password)
        
#         connection = get_db_connection()
#         if not connection:
#             return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
#         cursor = connection.cursor()
#         try:
#             # Verificar si el usuario ya existe
#             cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', 
#                           (username, email))
#             existing_user = cursor.fetchone()
            
#             if existing_user:
#                 return jsonify({"error": "El usuario o email ya existe"}), 400
            
#             # Insertar nuevo usuario
#             cursor.execute(
#                 'INSERT INTO users (username, password, email, role_id) VALUES (%s, %s, %s, %s)',
#                 (username, hashed_pw, email, 2)  # 2 = role 'user' por defecto
#             )
#             connection.commit()
            
#             return jsonify({"message": "Usuario creado exitosamente"}), 201
            
#         except mysql.connector.IntegrityError as e:
#             connection.rollback()
#             error_msg = str(e).lower()
#             if "username" in error_msg:
#                 return jsonify({"error": "El nombre de usuario ya existe"}), 400
#             elif "email" in error_msg:
#                 return jsonify({"error": "El email ya está registrado"}), 400
#             else:
#                 return jsonify({"error": "El usuario ya existe"}), 400
#         except Error as e:
#             connection.rollback()
#             print(f"Error en registro: {e}")
#             return jsonify({"error": "Error creando usuario"}), 500
#         finally:
#             cursor.close()
#             connection.close()
            
#     except Exception as e:
#         print(f"Error general en registro: {e}")
#         return jsonify({"error": "Error interno del servidor"}), 500

# Rutas de tareas (con CORS headers)
@app.route('/tasks', methods=['GET', 'OPTIONS'])
@token_required
def listar_tasks(current_user):
    if request.method == 'OPTIONS':
        return handle_preflight()
        
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        user = get_user_by_username(current_user)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        if user['role_id'] == 1:  # admin
            cursor.execute("""
                SELECT t.*, u.username as created_by_username 
                FROM tasks t 
                JOIN users u ON t.created_by = u.id 
                WHERE t.is_alive = TRUE 
                ORDER BY t.created_at DESC
            """)
        else:
            cursor.execute("""
                SELECT t.*, u.username as created_by_username 
                FROM tasks t 
                JOIN users u ON t.created_by = u.id 
                WHERE t.created_by = %s AND t.is_alive = TRUE 
                ORDER BY t.created_at DESC
            """, (user['id'],))
        
        tasks = cursor.fetchall()
        return jsonify({"tasks": tasks, "count": len(tasks)})
    except Error as e:
        return jsonify({"error": f"Error obteniendo tareas: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/task', methods=['POST', 'OPTIONS'])
@token_required
def crear_task(current_user):
    if request.method == 'OPTIONS':
        return handle_preflight()
        
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "Nombre de la tarea requerido"}), 400
    
    user = get_user_by_username(current_user)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    cursor = connection.cursor()
    try:
        deadline = None
        if data.get('deadline'):
            try:
                # Intentar múltiples formatos de fecha
                date_formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S.%f',
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                ]
                
                deadline_str = data['deadline']
                parsed_date = None
                
                for date_format in date_formats:
                    try:
                        parsed_date = datetime.strptime(deadline_str, date_format)
                        break
                    except ValueError:
                        continue
                
                if parsed_date:
                    deadline = parsed_date
                else:
                    return jsonify({"error": "Formato de deadline inválido"}), 400
                    
            except Exception as e:
                return jsonify({"error": f"Error procesando fecha: {str(e)}"}), 400
        
        cursor.execute("""
            INSERT INTO tasks (name, description, deadline, status, created_by) 
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data['name'],
            data.get('description', ''),
            deadline,
            data.get('status', 'In Progress'),
            user['id']
        ))
        
        connection.commit()
        task_id = cursor.lastrowid
        return jsonify({
            "message": "Tarea creada exitosamente",
            "task": {
                "id": task_id,
                "name": data['name'],
                "description": data.get('description', ''),
                "deadline": deadline.isoformat() if deadline else None,
                "status": data.get('status', 'In Progress'),
                "created_by": user['id']
            }
        }), 201
    except Error as e:
        return jsonify({"error": f"Error creando tarea: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/task/<int:task_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
@token_required
def task_operations(current_user, task_id):
    if request.method == 'OPTIONS':
        return handle_preflight()
        
    user = get_user_by_username(current_user)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Obtener tarea
        cursor.execute("""
            SELECT t.*, u.username as created_by_username 
            FROM tasks t 
            JOIN users u ON t.created_by = u.id 
            WHERE t.id = %s AND t.is_alive = TRUE
        """, (task_id,))
        
        task = cursor.fetchone()
        if not task:
            return jsonify({"error": "Tarea no encontrada"}), 404
        
        # Verificar permisos
        if user['role_id'] != 1 and task['created_by'] != user['id']:
            return jsonify({"error": "No tienes permisos para acceder a esta tarea"}), 403
        
        if request.method == 'GET':
            return jsonify({"task": task})
        
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({"error": "Datos requeridos"}), 400
            
            update_fields = []
            values = []
            
            if 'name' in data:
                update_fields.append('name = %s')
                values.append(data['name'])
            
            if 'description' in data:
                update_fields.append('description = %s')
                values.append(data['description'])
            
            if 'deadline' in data:
                if data['deadline']:
                    try:
                        # Usar los mismos formatos múltiples
                        date_formats = [
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%d %H:%M',
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%dT%H:%M:%S.%f',
                            '%Y-%m-%dT%H:%M:%S.%fZ'
                        ]
                        
                        deadline_str = data['deadline']
                        parsed_date = None
                        
                        for date_format in date_formats:
                            try:
                                parsed_date = datetime.strptime(deadline_str, date_format)
                                break
                            except ValueError:
                                continue
                        
                        if parsed_date:
                            update_fields.append('deadline = %s')
                            values.append(parsed_date)
                        else:
                            return jsonify({"error": "Formato de deadline inválido"}), 400
                            
                    except Exception as e:
                        return jsonify({"error": f"Error procesando fecha: {str(e)}"}), 400
                else:
                    update_fields.append('deadline = NULL')
            
            if 'status' in data:
                valid_statuses = ['In Progress', 'Revision', 'Completed', 'Paused']
                if data['status'] not in valid_statuses:
                    return jsonify({"error": f"Status inválido. Debe ser uno de: {valid_statuses}"}), 400
                update_fields.append('status = %s')
                values.append(data['status'])
            
            if not update_fields:
                return jsonify({"error": "No hay campos para actualizar"}), 400
            
            values.append(task_id)
            query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(query, values)
            connection.commit()
            
            return jsonify({"message": "Tarea actualizada exitosamente"})
        
        elif request.method == 'DELETE':
            cursor.execute('UPDATE tasks SET is_alive = FALSE WHERE id = %s', (task_id,))
            connection.commit()
            return jsonify({"message": "Tarea eliminada exitosamente"})
    
    except Error as e:
        return jsonify({"error": f"Error en operación: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/tasks/status/<status>', methods=['GET', 'OPTIONS'])
@token_required
def tasks_by_status(current_user, status):
    if request.method == 'OPTIONS':
        return handle_preflight()
    # ... resto de la implementación similar a listar_tasks pero filtrando por status

@app.route('/info', methods=['GET', 'OPTIONS'])
@token_required
def info(current_user):
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    return jsonify({
        "service": "Task Management Service",
        "version": "1.0.0",
        "user": current_user,
        "endpoints": ["/tasks", "/task", "/login", "/register"]
    })

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    return jsonify({"status": "OK", "service": "Task Service"}), 200

if __name__ == '__main__':
    print("=" * 50)
    print("INICIANDO TASK SERVICE")
    print("=" * 50)
    print("Task Service URL: http://localhost:5003")
    print("CORS configurado para: http://localhost:4200, http://localhost:4000")
    print("=" * 50)
    app.run(port=5003, debug=True)