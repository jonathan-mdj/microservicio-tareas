from user_service.app_mongo import app
from database_mongo import mongo_db

def test_user_service():
    print("🧪 Probando User Service MongoDB...")
    
    try:
        # Probar endpoint /health
        print("\n1️⃣ Probando endpoint /health...")
        with app.test_client() as client:
            response = client.get('/health')
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.get_json()}")
        
        # Probar endpoint /users
        print("\n2️⃣ Probando endpoint /users...")
        with app.test_client() as client:
            response = client.get('/users')
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            print(f"   Usuarios encontrados: {data.get('count', 0)}")
            if data.get('users'):
                for user in data['users']:
                    print(f"     - {user['username']} ({user.get('email', 'N/A')}) - {user['role']}")
        
        # Probar endpoint /roles
        print("\n3️⃣ Probando endpoint /roles...")
        with app.test_client() as client:
            response = client.get('/roles')
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            print(f"   Roles encontrados: {data.get('count', 0)}")
            if data.get('roles'):
                for role in data['roles']:
                    print(f"     - {role['nombre']} (ID: {role['id']})")
        
        # Probar endpoint root
        print("\n4️⃣ Probando endpoint root...")
        with app.test_client() as client:
            response = client.get('/')
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            print(f"   Service: {data.get('service')}")
            print(f"   Database: {data.get('database')}")
            print(f"   Port: {data.get('port')}")
        
        print("\n🎉 Pruebas del User Service completadas!")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_service()
