from database_mongo import mongo_db
from datetime import datetime
import bcrypt

def migrate_data():
    print("🚀 Iniciando migración a MongoDB...")
    
    try:
        # Conectar a MongoDB
        if not mongo_db.connect():
            print("❌ No se pudo conectar a MongoDB")
            return False
        
        # 1. Crear usuario profesor (admin)
        users_collection = mongo_db.get_collection('users')
        
        # Hash password para el profesor
        password = "Pr@f123456"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        admin_user = {
            "_id": 1,
            "username": "Profesor",
            "email": "prof@gmail.com",
            "password": hashed_password.decode('utf-8'),
            "role": "admin",
            "otp_secret": None,
            "require_otp": False,
            "created_at": datetime.utcnow()
        }
        
        # Insertar usuario admin
        try:
            # Verificar si ya existe
            existing_user = users_collection.find_one({"email": "prof@gmail.com"})
            if existing_user:
                print("✅ Usuario admin ya existe")
            else:
                users_collection.insert_one(admin_user)
                print("✅ Usuario admin creado exitosamente")
        except Exception as e:
            print(f"⚠️ Usuario admin ya existe o error: {e}")
        
        # 2. Crear colección de tareas
        tasks_collection = mongo_db.get_collection('tasks')
        
        # Crear índices para mejor performance
        try:
            tasks_collection.create_index("user_id")
            tasks_collection.create_index("status")
            tasks_collection.create_index("created_at")
            print("✅ Índices de tareas creados")
        except Exception as e:
            print(f"⚠️ Error creando índices: {e}")
        
        # 3. Crear colección de roles
        roles_collection = mongo_db.get_collection('roles')
        
        # Insertar roles básicos
        basic_roles = [
            {"_id": 1, "name": "admin", "description": "Administrador del sistema"},
            {"_id": 2, "name": "user", "description": "Usuario estándar"}
        ]
        
        for role in basic_roles:
            try:
                existing_role = roles_collection.find_one({"_id": role["_id"]})
                if not existing_role:
                    roles_collection.insert_one(role)
                    print(f"✅ Rol {role['name']} creado")
                else:
                    print(f"✅ Rol {role['name']} ya existe")
            except Exception as e:
                print(f"⚠️ Error creando rol {role['name']}: {e}")
        
        print("\n🎉 Migración completada exitosamente!")
        print("📋 Datos creados:")
        print("   - Usuario: prof@gmail.com")
        print("   - Password: Pr@f123456")
        print("   - Rol: admin")
        print("   - Colecciones: users, tasks, roles")
        print("   - Índices: user_id, status, created_at")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

if __name__ == "__main__":
    migrate_data()
