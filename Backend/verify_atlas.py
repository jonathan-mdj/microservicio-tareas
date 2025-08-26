# verify_atlas.py - Verificar conexión y datos en MongoDB Atlas
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Cargar variables de entorno
load_dotenv('.env.atlas')

def verify_atlas_connection():
    """Verificar conexión a MongoDB Atlas"""
    print("🔍 Verificando conexión a MongoDB Atlas...")
    
    try:
        # Obtener URI de Atlas
        atlas_uri = os.getenv('MONGO_URI_ATLAS')
        if not atlas_uri:
            print("❌ MONGO_URI_ATLAS no configurada")
            return False
        
        # Conectar a Atlas
        client = MongoClient(atlas_uri)
        db = client['task_management']
        
        # Verificar conexión
        client.admin.command('ismaster')
        print("✅ Conexión a MongoDB Atlas exitosa")
        
        return client, db
        
    except Exception as e:
        print(f"❌ Error conectando a MongoDB Atlas: {e}")
        return False

def verify_collections(db):
    """Verificar que las colecciones existan en Atlas"""
    print("\n📊 Verificando colecciones en Atlas...")
    
    try:
        collections = db.list_collection_names()
        print(f"   Colecciones encontradas: {collections}")
        
        required_collections = ['users', 'tasks', 'roles']
        missing_collections = [col for col in required_collections if col not in collections]
        
        if missing_collections:
            print(f"   ⚠️ Colecciones faltantes: {missing_collections}")
            return False
        else:
            print("   ✅ Todas las colecciones requeridas existen")
            return True
            
    except Exception as e:
        print(f"❌ Error verificando colecciones: {e}")
        return False

def verify_users(db):
    """Verificar usuarios en Atlas"""
    print("\n👥 Verificando usuarios en Atlas...")
    
    try:
        users = list(db.users.find({}, {"password": 0, "otp_secret": 0}))
        print(f"   Total usuarios: {len(users)}")
        
        if users:
            print("   Usuarios encontrados:")
            for user in users:
                print(f"     - {user['username']} ({user.get('email', 'N/A')}) - {user.get('role', 'user')}")
        else:
            print("   ⚠️ No hay usuarios en Atlas")
            
        return len(users)
        
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")
        return 0

def verify_tasks(db):
    """Verificar tareas en Atlas"""
    print("\n📋 Verificando tareas en Atlas...")
    
    try:
        tasks = list(db.tasks.find({"is_alive": True}))
        print(f"   Total tareas: {len(tasks)}")
        
        if tasks:
            print("   Tareas encontradas:")
            for task in tasks:
                print(f"     - {task['name']} - {task.get('status', 'N/A')}")
        else:
            print("   ⚠️ No hay tareas en Atlas")
            
        return len(tasks)
        
    except Exception as e:
        print(f"❌ Error verificando tareas: {e}")
        return 0

def verify_roles(db):
    """Verificar roles en Atlas"""
    print("\n🔐 Verificando roles en Atlas...")
    
    try:
        roles = list(db.roles.find({}))
        print(f"   Total roles: {len(roles)}")
        
        if roles:
            print("   Roles encontrados:")
            for role in roles:
                print(f"     - {role['name']}")
        else:
            print("   ⚠️ No hay roles en Atlas")
            
        return len(roles)
        
    except Exception as e:
        print(f"❌ Error verificando roles: {e}")
        return 0

def verify_indices(db):
    """Verificar índices en Atlas"""
    print("\n📊 Verificando índices en Atlas...")
    
    try:
        # Verificar índices de usuarios
        user_indices = list(db.users.list_indexes())
        print(f"   Índices de usuarios: {len(user_indices)}")
        
        # Verificar índices de tareas
        task_indices = list(db.tasks.list_indexes())
        print(f"   Índices de tareas: {len(task_indices)}")
        
        # Verificar índices de roles
        role_indices = list(db.roles.list_indexes())
        print(f"   Índices de roles: {len(role_indices)}")
        
        print("   ✅ Verificación de índices completada")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando índices: {e}")
        return False

def test_atlas_operations(db):
    """Probar operaciones básicas en Atlas"""
    print("\n🧪 Probando operaciones básicas en Atlas...")
    
    try:
        # Probar lectura
        user_count = db.users.count_documents({})
        print(f"   ✅ Lectura exitosa - Usuarios: {user_count}")
        
        # Probar escritura (crear documento temporal)
        test_doc = {
            "test": True,
            "timestamp": datetime.utcnow(),
            "message": "Prueba de escritura en Atlas"
        }
        
        result = db.test_collection.insert_one(test_doc)
        print(f"   ✅ Escritura exitosa - ID: {result.inserted_id}")
        
        # Limpiar documento de prueba
        db.test_collection.delete_one({"_id": result.inserted_id})
        print("   ✅ Limpieza exitosa")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en operaciones de prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN COMPLETA DE MONGODB ATLAS")
    print("=" * 50)
    
    # Verificar archivo de configuración
    if not os.path.exists('.env.atlas'):
        print("❌ Archivo .env.atlas no encontrado")
        print("📝 Crea el archivo .env.atlas basándote en env_atlas_example.txt")
        return
    
    # Verificar conexión
    connection_result = verify_atlas_connection()
    if not connection_result:
        print("❌ No se pudo conectar a MongoDB Atlas")
        return
    
    client, db = connection_result
    
    try:
        # Verificaciones
        collections_ok = verify_collections(db)
        users_count = verify_users(db)
        tasks_count = verify_tasks(db)
        roles_count = verify_roles(db)
        indices_ok = verify_indices(db)
        operations_ok = test_atlas_operations(db)
        
        # Resumen
        print("\n" + "=" * 50)
        print("📋 RESUMEN DE VERIFICACIÓN")
        print("=" * 50)
        print(f"   🔌 Conexión: ✅ EXITOSA")
        print(f"   📊 Colecciones: {'✅ OK' if collections_ok else '❌ FALLO'}")
        print(f"   👥 Usuarios: {users_count}")
        print(f"   📋 Tareas: {tasks_count}")
        print(f"   🔐 Roles: {roles_count}")
        print(f"   📊 Índices: {'✅ OK' if indices_ok else '❌ FALLO'}")
        print(f"   🧪 Operaciones: {'✅ OK' if operations_ok else '❌ FALLO'}")
        
        if all([collections_ok, indices_ok, operations_ok]):
            print("\n🎉 MongoDB Atlas está funcionando correctamente")
            print("🌐 Puedes proceder con el despliegue a producción")
        else:
            print("\n⚠️ Hay problemas con MongoDB Atlas")
            print("🔍 Revisa los errores antes de continuar")
            
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
    
    finally:
        # Cerrar conexión
        if client:
            client.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    main()
