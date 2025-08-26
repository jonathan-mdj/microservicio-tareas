from auth_service.app_mongo import app

def test_register():
    print("🧪 Probando registro de usuarios en MongoDB...")
    
    try:
        # Probar registro de usuario nuevo
        print("\n1️⃣ Probando registro de usuario nuevo...")
        with app.test_client() as client:
            user_data = {
                "username": "testuser",
                "password": "Test123!",
                "email": "test@example.com"
            }
            response = client.post('/register', json=user_data)
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            if response.status_code == 201:
                print(f"   ✅ Usuario creado exitosamente")
                print(f"   User ID: {data.get('user_id')}")
                print(f"   OTP Secret: {data.get('otp_secret')}")
                print(f"   QR Code: {'Sí' if data.get('qr_code') else 'No'}")
            else:
                print(f"   ❌ Error en registro: {data.get('error')}")
        
        # Probar login del usuario recién creado (con OTP)
        print("\n2️⃣ Probando login del usuario nuevo...")
        with app.test_client() as client:
            # Primero necesitamos generar un OTP válido
            import pyotp
            otp_secret = "JBSWY3DPEHPK3PXP"  # Secret de prueba
            totp = pyotp.TOTP(otp_secret)
            current_otp = totp.now()
            
            login_data = {
                "username": "testuser",
                "password": "Test123!",
                "otp": current_otp
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
        
        print("\n🎉 Pruebas de registro completadas!")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_register()
