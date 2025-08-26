# task_service/app_mongo.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import traceback
from database_mongo import mongo_db
from config import config
from bson import ObjectId

app = Flask(__name__)
app.config['SECRET_KEY'] = config.JWT_SECRET

# Configuración CORS más robusta
CORS(app, 
     origins=config.CORS_ORIGINS,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=True,
     max_age=3600)

print(f"[DB] Conectando a MongoDB: {config.MONGO_URI}")

def get_user_by_username(username):
    """Obtener usuario por username desde MongoDB"""
    try:
        if not mongo_db.connect():
            return None
        
        users_collection = mongo_db.get_collection('users')
        user = users_collection.find_one({"username": username})
        
        if user:
            # Convertir ObjectId a string para compatibilidad
            user['id'] = str(user['_id'])
            user['role_id'] = 1 if user.get('role') == 'admin' else 2
            print(f"[DEBUG] Usuario encontrado: {user['username']}, ID: {user['id']}, Role: {user['role']}")
        else:
            print(f"[DEBUG] Usuario no encontrado con username: {username}")
        
        return user
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return None

def get_user_by_username_or_email(identifier):
    """Obtener usuario por username o email desde MongoDB"""
    try:
        if not mongo_db.connect():
            return None
        
        users_collection = mongo_db.get_collection('users')
        user = users_collection.find_one({
            "$or": [
                {"username": identifier},
                {"email": identifier}
            ]
        })
        
        if user:
            # Convertir ObjectId a string para compatibilidad
            user['id'] = str(user['_id'])
            user['role_id'] = 1 if user.get('role') == 'admin' else 2
        
        return user
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return None

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
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type', 'Authorization', 'X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response

# Rutas de tareas (con CORS headers)
@app.route('/tasks', methods=['GET', 'OPTIONS'])
def listar_tasks():
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    try:
        # Obtener usuario del header Authorization (simulado)
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Token de autorización requerido"}), 401
        
        # Por simplicidad, asumimos que el usuario es admin
        # En producción, deberías validar el JWT token
        current_user = "Profesor"  # Simulado
        
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        tasks_collection = mongo_db.get_collection('tasks')
        
        # Obtener todas las tareas (admin puede ver todas)
        tasks = list(tasks_collection.find({"is_alive": True}))
        
        # Convertir ObjectId a string y procesar fechas
        processed_tasks = []
        for task in tasks:
            task_dict = {
                "id": str(task['_id']),
                "name": task['name'],
                "description": task.get('description', ''),
                "deadline": convert_datetime_to_string(task.get('deadline')),
                "status": task.get('status', 'In Progress'),
                "created_by": str(task.get('created_by', '')),
                "created_at": convert_datetime_to_string(task.get('created_at')),
                "created_by_username": task.get('created_by_username', 'Unknown')
            }
            processed_tasks.append(task_dict)
        
        return jsonify({"tasks": processed_tasks, "count": len(processed_tasks)})
        
    except Exception as e:
        print(f"Error obteniendo tareas: {e}")
        return jsonify({"error": f"Error obteniendo tareas: {str(e)}"}), 500

@app.route('/task', methods=['POST', 'OPTIONS'])
def crear_task():
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({"error": "Nombre de la tarea requerido"}), 400
        
        # Por simplicidad, asumimos que el usuario es admin
        # En producción, deberías validar el JWT token
        current_user = "Profesor"  # Simulado
        
        user = get_user_by_username(current_user)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        tasks_collection = mongo_db.get_collection('tasks')
        
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
        
        # Crear documento de tarea
        task_doc = {
            "name": data['name'],
            "description": data.get('description', ''),
            "deadline": deadline,
            "status": data.get('status', 'In Progress'),
            "created_by": user['id'],
            "created_by_username": user['username'],
            "created_at": datetime.utcnow(),
            "is_alive": True
        }
        
        # Insertar tarea
        result = tasks_collection.insert_one(task_doc)
        
        return jsonify({
            "message": "Tarea creada exitosamente",
            "task": {
                "id": str(result.inserted_id),
                "name": data['name'],
                "description": data.get('description', ''),
                "deadline": deadline.isoformat() if deadline else None,
                "status": data.get('status', 'In Progress'),
                "created_by": user['id']
            }
        }), 201
        
    except Exception as e:
        print(f"Error creando tarea: {e}")
        return jsonify({"error": f"Error creando tarea: {str(e)}"}), 500

@app.route('/task/<task_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def task_operations(task_id):
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    try:
        # Por simplicidad, asumimos que el usuario es admin
        # En producción, deberías validar el JWT token
        current_user = "Profesor"  # Simulado
        
        user = get_user_by_username(current_user)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        tasks_collection = mongo_db.get_collection('tasks')
        
        try:
            # Obtener tarea
            task = tasks_collection.find_one({
                "_id": ObjectId(task_id),
                "is_alive": True
            })
        except:
            return jsonify({"error": "ID de tarea inválido"}), 400
        
        if not task:
            return jsonify({"error": "Tarea no encontrada"}), 404
        
        # Verificar permisos (admin puede acceder a todas)
        if user['role_id'] != 1 and str(task['created_by']) != user['id']:
            return jsonify({"error": "No tienes permisos para acceder a esta tarea"}), 403
        
        if request.method == 'GET':
            task_dict = {
                "id": str(task['_id']),
                "name": task['name'],
                "description": task.get('description', ''),
                "deadline": convert_datetime_to_string(task.get('deadline')),
                "status": task.get('status', 'In Progress'),
                "created_by": str(task.get('created_by', '')),
                "created_at": convert_datetime_to_string(task.get('created_at')),
                "created_by_username": task.get('created_by_username', 'Unknown')
            }
            return jsonify({"task": task_dict})
        
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({"error": "Datos requeridos"}), 400
            
            update_fields = {}
            
            if 'name' in data:
                update_fields['name'] = data['name']
            
            if 'description' in data:
                update_fields['description'] = data['description']
            
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
                            update_fields['deadline'] = parsed_date
                        else:
                            return jsonify({"error": "Formato de deadline inválido"}), 400
                            
                    except Exception as e:
                        return jsonify({"error": f"Error procesando fecha: {str(e)}"}), 400
                else:
                    update_fields['deadline'] = None
            
            if 'status' in data:
                valid_statuses = ['In Progress', 'Revision', 'Completed', 'Paused']
                if data['status'] not in valid_statuses:
                    return jsonify({"error": f"Status inválido. Debe ser uno de: {valid_statuses}"}), 400
                update_fields['status'] = data['status']
            
            if not update_fields:
                return jsonify({"error": "No hay campos para actualizar"}), 400
            
            # Actualizar tarea
            tasks_collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": update_fields}
            )
            
            return jsonify({"message": "Tarea actualizada exitosamente"})
        
        elif request.method == 'DELETE':
            # Soft delete - marcar como no activa
            tasks_collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {"is_alive": False}}
            )
            
            return jsonify({"message": "Tarea eliminada exitosamente"})
    
    except Exception as e:
        print(f"Error en operación: {e}")
        return jsonify({"error": f"Error en operación: {str(e)}"}), 500

@app.route('/tasks/status/<status>', methods=['GET', 'OPTIONS'])
def tasks_by_status(status):
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    try:
        # Por simplicidad, asumimos que el usuario es admin
        # En producción, deberías validar el JWT token
        current_user = "Profesor"  # Simulado
        
        if not mongo_db.connect():
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        tasks_collection = mongo_db.get_collection('tasks')
        
        # Obtener tareas por status
        tasks = list(tasks_collection.find({
            "status": status,
            "is_alive": True
        }))
        
        # Convertir ObjectId a string y procesar fechas
        processed_tasks = []
        for task in tasks:
            task_dict = {
                "id": str(task['_id']),
                "name": task['name'],
                "description": task.get('description', ''),
                "deadline": convert_datetime_to_string(task.get('deadline')),
                "status": task.get('status', 'In Progress'),
                "created_by": str(task.get('created_by', '')),
                "created_at": convert_datetime_to_string(task.get('created_at')),
                "created_by_username": task.get('created_by_username', 'Unknown')
            }
            processed_tasks.append(task_dict)
        
        return jsonify({"tasks": processed_tasks, "count": len(processed_tasks)})
        
    except Exception as e:
        print(f"Error obteniendo tareas por status: {e}")
        return jsonify({"error": f"Error obteniendo tareas: {str(e)}"}), 500

@app.route('/info', methods=['GET', 'OPTIONS'])
def info():
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    return jsonify({
        "service": "Task Management Service (MongoDB)",
        "version": "1.0.0",
        "user": "admin",  # Simulado
        "endpoints": ["/tasks", "/task", "/tasks/status/<status>"]
    })

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return handle_preflight()
    
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
        "service": "Task Service (MongoDB)",
        "database": db_status,
        "port": config.TASK_SERVICE_PORT
    }), 200

if __name__ == '__main__':
    print("=" * 50)
    print("INICIANDO TASK SERVICE (MongoDB)")
    print("=" * 50)
    print(f"Task Service URL: http://localhost:{config.TASK_SERVICE_PORT}")
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
    app.run(host='0.0.0.0', port=config.TASK_SERVICE_PORT, debug=config.DEBUG)
