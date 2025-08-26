from database_mongo import mongo_db

def list_users():
    print("👥 Listando todos los usuarios en MongoDB...")
    
    try:
        mongo_db.connect()
        users_collection = mongo_db.get_collection('users')
        
        # Obtener todos los usuarios
        users = list(users_collection.find({}, {
            "password": 0,  # Excluir password
            "otp_secret": 0  # Excluir OTP secret
        }))
        
        print(f"\n📊 Total de usuarios: {len(users)}")
        
        for i, user in enumerate(users, 1):
            print(f"\n{i}. Usuario:")
            print(f"   ID: {user['_id']}")
            print(f"   Username: {user['username']}")
            print(f"   Email: {user.get('email', 'N/A')}")
            print(f"   Role: {user['role']}")
            print(f"   Require OTP: {user.get('require_otp', 'N/A')}")
            print(f"   Created: {user.get('created_at', 'N/A')}")
        
        print("\n🎉 Listado completado!")
        
    except Exception as e:
        print(f"❌ Error listando usuarios: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_users()
