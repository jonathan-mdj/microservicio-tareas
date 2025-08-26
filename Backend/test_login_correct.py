from auth_service.app_mongo import app
from database_mongo import mongo_db
import pyotp

def test_login_correct():
    print("🧪 Probando login del usuario testuser con OTP correcto...")
    
    try:
        # Obtener el OTP secret del usuario testuser
        mongo_db.connect()
        users_collection = mongo_db.get_collection('users')
        user = users_collection.find_one({"username": "testuser"})
        
        if not user:
            print("❌ Usuario testuser no encontrado")
            return
        
        otp_secret = user['otp_secret']
        print(f"   OTP Secret encontrado: {otp_secret}")
        
        # Generar OTP válido
        totp = pyotp.TOTP(otp_secret)
        current_otp = totp.now()
        print(f"   OTP generado: {current_otp}")
        
        # Probar login
        print("\n🔐 Probando login...")
        with app.test_client() as client:
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
                print(f"   Role: {data.get('user', {}).get('role')}")
            else:
                print(f"   ❌ Login falló: {data.get('error')}")
        
        print("\n🎉 Prueba de login completada!")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_correct()
