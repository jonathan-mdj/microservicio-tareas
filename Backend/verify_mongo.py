from database_mongo import mongo_db

def verify_data():
    print("🔍 Verificando datos en MongoDB...")
    
    try:
        mongo_db.connect()
        
        # Verificar usuario admin
        users = mongo_db.get_collection('users')
        admin_user = users.find_one({'email': 'prof@gmail.com'})
        
        if admin_user:
            print("✅ Usuario admin encontrado:")
            print(f"   Username: {admin_user['username']}")
            print(f"   Email: {admin_user['email']}")
            print(f"   Role: {admin_user['role']}")
            print(f"   Require OTP: {admin_user['require_otp']}")
        else:
            print("❌ Usuario admin no encontrado")
        
        # Verificar colecciones
        collections = mongo_db.db.list_collection_names()
        print(f"\n📚 Colecciones creadas: {collections}")
        
        # Verificar índices de tareas
        tasks = mongo_db.get_collection('tasks')
        indexes = tasks.list_indexes()
        print("\n📊 Índices de tareas:")
        for index in indexes:
            print(f"   - {index['name']}: {index['key']}")
        
        print("\n🎉 Verificación completada!")
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")

if __name__ == "__main__":
    verify_data()
