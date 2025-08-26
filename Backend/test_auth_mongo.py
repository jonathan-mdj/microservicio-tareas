from auth_service.app_mongo import app
from database_mongo import mongo_db

def test_auth_service():
    print("🧪 Probando Auth Service MongoDB...")
    
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
                    print(f"     - {user['username']} ({user['email']}) - {user['role']}")
        
        # Probar login del Profesor (sin OTP)
        print("\n3️⃣ Probando login del Profesor...")
        with app.test_client() as client:
            login_data = {
                "username": "prof@gmail.com",
                "password": "Pr@f123456"
            }
            response = client.post('/login', json=login_data)
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            if response.status_code == 200:
                print(f"   ✅ Login exitoso: {data.get('message')}")
                print(f"   Token recibido: {'Sí' if data.get('token') else 'No'}")
                print(f"   Usuario: {data.get('user', {}).get('username')}")
            else:
                print(f"   ❌ Login falló: {data.get('error')}")
        
        print("\n🎉 Pruebas completadas!")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth_service()
