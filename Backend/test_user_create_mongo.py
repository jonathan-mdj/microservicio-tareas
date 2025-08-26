from user_service.app_mongo import app

def test_user_creation():
    print("🧪 Probando creación de usuarios en User Service MongoDB...")
    
    try:
        # Probar creación de usuario nuevo
        print("\n1️⃣ Probando creación de usuario nuevo...")
        with app.test_client() as client:
            user_data = {
                "username": "newuser",
                "password": "NewPass123!",
                "email": "newuser@example.com",
                "role": "user"
            }
            response = client.post('/users', json=user_data)
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            if response.status_code == 201:
                print(f"   ✅ Usuario creado exitosamente")
                print(f"   User ID: {data.get('user', {}).get('id')}")
                print(f"   Username: {data.get('user', {}).get('username')}")
                print(f"   Email: {data.get('user', {}).get('email')}")
                print(f"   Role: {data.get('user', {}).get('role')}")
            else:
                print(f"   ❌ Error en creación: {data.get('error')}")
        
        # Verificar que el usuario se creó
        print("\n2️⃣ Verificando usuario creado...")
        with app.test_client() as client:
            response = client.get('/users')
            data = response.get_json()
            print(f"   Total usuarios: {data.get('count', 0)}")
            if data.get('users'):
                for user in data['users']:
                    if user['username'] == 'newuser':
                        print(f"   ✅ Usuario 'newuser' encontrado en la lista")
                        break
                else:
                    print(f"   ❌ Usuario 'newuser' no encontrado en la lista")
        
        print("\n🎉 Pruebas de creación completadas!")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_creation()
