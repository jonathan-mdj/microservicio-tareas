# user_service/app_mongo.py
from flask import Flask, jsonify, request
import bcrypt
import os
from datetime import datetime
import traceback
from database_mongo import mongo_db
from config import config

app = Flask(__name__)



print(f"[DB] Conectando a MongoDB: {config.MONGO_URI}")

def hash_password(password):
    """Hashear contraseña usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def convert_datetime_to_string(obj):
    """Convertir datetime a string de forma segura"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj) if obj is not None else None

# CORS manejado por API Gateway - no configurar aquí

@app.route('/users', methods=['GET', 'OPTIONS'])
def get_users():
    """Obtener lista de todos los usuarios desde MongoDB"""
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
        
        # Convertir ObjectId a string para JSON y procesar fechas
        processed_users = []
        for user in users:
            user_dict = {
                "id": str(user['_id']),
                "username": user['username'],
                "email": user.get('email'),
                "role": user.get('role', 'user'),
                "created_at": convert_datetime_to_string(user.get('created_at'))
            }
            processed_users.append(user_dict)
        
        return jsonify({"users": processed_users, "count": len(processed_users)}), 200
        
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return jsonify({"error": "Error obteniendo usuarios"}), 500

@app.route('/users/<user_id>', methods=['GET', 'OPTIONS'])
def get_user(user_id):
    """Obtener un usuario específico por ID desde MongoDB"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    try:
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        users_collection = mongo_db.get_collection('users')
        
        # Buscar usuario por ID
        from bson import ObjectId
        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)}, {
                "password": 0,  # Excluir password
                "otp_secret": 0  # Excluir OTP secret
            })
        except:
            return jsonify({"error": "ID de usuario inválido"}), 400
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Convertir a formato de respuesta
        user_dict = {
            "id": str(user['_id']),
            "username": user['username'],
            "email": user.get('email'),
            "role": user.get('role', 'user'),
            "created_at": convert_datetime_to_string(user.get('created_at'))
        }
        
        return jsonify({"user": user_dict}), 200
        
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return jsonify({"error": "Error obteniendo usuario"}), 500

@app.route('/users', methods=['POST', 'OPTIONS'])
def create_user():
    """Crear un nuevo usuario en MongoDB"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
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
        role = data.get('role', 'user')  # user por defecto
        
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
        
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        users_collection = mongo_db.get_collection('users')
        
        try:
            # Verificar si el usuario ya existe
            existing_user = users_collection.find_one({
                "$or": [
                    {"username": username},
                    {"email": email} if email else {"username": "nonexistent"}
                ]
            })
            
            if existing_user:
                return jsonify({"error": "El usuario o email ya existe"}), 400
            
            # Crear documento de usuario
            user_doc = {
                "username": username,
                "password": hashed_pw.decode('utf-8'),
                "email": email,
                "role": role,
                "created_at": datetime.utcnow()
            }
            
            # Insertar usuario
            result = users_collection.insert_one(user_doc)
            
            # Obtener información del usuario creado
            new_user = users_collection.find_one({"_id": result.inserted_id}, {
                "password": 0,
                "otp_secret": 0
            })
            
            user_data = {
                "id": str(new_user['_id']),
                "username": new_user['username'],
                "email": new_user.get('email'),
                "role": new_user.get('role', 'user'),
                "created_at": convert_datetime_to_string(new_user.get('created_at'))
            }
            
            return jsonify({
                "message": "Usuario creado exitosamente",
                "user": user_data
            }), 201
            
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return jsonify({"error": "Error creando usuario"}), 500
            
    except Exception as e:
        print(f"Error general creando usuario: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/users/<user_id>', methods=['PUT', 'OPTIONS'])
def update_user(user_id):
    """Actualizar un usuario existente en MongoDB"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        users_collection = mongo_db.get_collection('users')
        
        try:
            # Verificar si el usuario existe
            from bson import ObjectId
            try:
                existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
            except:
                return jsonify({"error": "ID de usuario inválido"}), 400
            
            if not existing_user:
                return jsonify({"error": "Usuario no encontrado"}), 404
            
            # Preparar campos para actualizar
            update_fields = {}
            
            if 'username' in data and data['username'].strip():
                new_username = data['username'].strip()
                # Verificar que el nuevo username no esté en uso
                if new_username != existing_user['username']:
                    username_exists = users_collection.find_one({"username": new_username})
                    if username_exists:
                        return jsonify({"error": "El nombre de usuario ya está en uso"}), 400
                update_fields['username'] = new_username
            
            if 'email' in data:
                new_email = data['email'].strip() if data['email'] else None
                if new_email != existing_user.get('email'):
                    if new_email:
                        # Validar formato de email
                        import re
                        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                        if not re.match(email_pattern, new_email):
                            return jsonify({"error": "El email no tiene un formato válido"}), 400
                        
                        # Verificar que el nuevo email no esté en uso
                        email_exists = users_collection.find_one({"email": new_email})
                        if email_exists:
                            return jsonify({"error": "El email ya está registrado"}), 400
                    update_fields['email'] = new_email
            
            if 'role' in data and data['role']:
                update_fields['role'] = data['role']
            
            if not update_fields:
                return jsonify({"error": "No hay campos para actualizar"}), 400
            
            # Actualizar usuario
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_fields}
            )
            
            # Obtener usuario actualizado
            updated_user = users_collection.find_one({"_id": ObjectId(user_id)}, {
                "password": 0,
                "otp_secret": 0
            })
            
            user_data = {
                "id": str(updated_user['_id']),
                "username": updated_user['username'],
                "email": updated_user.get('email'),
                "role": updated_user.get('role', 'user'),
                "created_at": convert_datetime_to_string(updated_user.get('created_at'))
            }
            
            return jsonify({
                "message": "Usuario actualizado exitosamente",
                "user": user_data
            }), 200
            
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            return jsonify({"error": "Error actualizando usuario"}), 500
            
    except Exception as e:
        print(f"Error general actualizando usuario: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/users/<user_id>', methods=['DELETE', 'OPTIONS'])
def delete_user(user_id):
    """Eliminar un usuario desde MongoDB"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    try:
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        users_collection = mongo_db.get_collection('users')
        
        try:
            # Verificar si el usuario existe
            from bson import ObjectId
            try:
                existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
            except:
                return jsonify({"error": "ID de usuario inválido"}), 400
            
            if not existing_user:
                return jsonify({"error": "Usuario no encontrado"}), 404
            
            # Eliminar usuario
            users_collection.delete_one({"_id": ObjectId(user_id)})
            
            return jsonify({"message": "Usuario eliminado exitosamente"}), 200
            
        except Exception as e:
            print(f"Error eliminando usuario: {e}")
            return jsonify({"error": "Error eliminando usuario"}), 500
            
    except Exception as e:
        print(f"Error general eliminando usuario: {e}")
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
    
    return jsonify({
        "status": "UP" if db_status == "UP" else "DEGRADED",
        "service": "User Service (MongoDB)",
        "database": db_status,
        "port": config.USER_SERVICE_PORT
    }), 200

@app.route('/roles', methods=['GET', 'OPTIONS'])
def get_roles():
    """Obtener roles desde MongoDB"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    try:
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        roles_collection = mongo_db.get_collection('roles')
        
        # Obtener roles
        roles = list(roles_collection.find({}, {"_id": 1, "name": 1}))
        
        # Convertir ObjectId a string
        for role in roles:
            role['id'] = str(role['_id'])
            role['nombre'] = role.get('name', '')
            del role['_id']
            del role['name']
        
        return jsonify({"roles": roles, "count": len(roles)})
        
    except Exception as e:
        return jsonify({"error": f"Error obteniendo roles: {str(e)}"}), 500

@app.route('/', methods=['GET', 'OPTIONS'])
def root():
    """Información del servicio"""
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'})
    
    return jsonify({
        "service": "User Service (MongoDB)",
        "version": "1.0.0",
        "port": config.USER_SERVICE_PORT,
        "endpoints": {
            "list_users": "GET /users",
            "get_user": "GET /users/{id}",
            "create_user": "POST /users",
            "update_user": "PUT /users/{id}",
            "delete_user": "DELETE /users/{id}",
            "get_roles": "GET /roles",
            "health": "GET /health"
        },
        "database": "MongoDB task_management"
    }), 200

if __name__ == '__main__':
    print("=" * 50)
    print("INICIANDO USER SERVICE (MongoDB)")
    print("=" * 50)
    print(f"User Service URL: http://localhost:{config.USER_SERVICE_PORT}")
    print("Base de datos: MongoDB task_management")
    print(f"CORS configurado para: {config.CORS_ORIGINS}")
    print("=" * 50)
    
    # Verificar conexión a MongoDB al iniciar
    if mongo_db.connect():
        print("✓ Conexión a MongoDB exitosa")
    else:
        print("✗ Error conectando a MongoDB")
        print("Verifica la configuración de la base de datos")
    
    print("=" * 50)
    app.run(host='0.0.0.0', port=config.USER_SERVICE_PORT, debug=config.DEBUG)
