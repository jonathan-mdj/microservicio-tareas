from api_gateway.app_mongo import app

def test_api_gateway():
    print("🧪 Probando API Gateway MongoDB...")
    
    try:
        # Probar endpoint raíz
        print("\n1️⃣ Probando endpoint raíz...")
        with app.test_client() as client:
            response = client.get('/')
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            print(f"   Service: {data.get('service')}")
            print(f"   Database: {data.get('database')}")
            print(f"   Version: {data.get('version')}")
        
        # Probar endpoint /health
        print("\n2️⃣ Probando endpoint /health...")
        with app.test_client() as client:
            response = client.get('/health')
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Database: {data.get('database')}")
        
        # Probar endpoint /logs/stats
        print("\n3️⃣ Probando endpoint /logs/stats...")
        with app.test_client() as client:
            response = client.get('/logs/stats')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Success: {data.get('success')}")
                print(f"   Total requests: {data.get('data', {}).get('total_requests', 0)}")
            else:
                data = response.get_json()
                print(f"   Error: {data.get('error')}")
        
        # Probar proxy a Auth Service
        print("\n4️⃣ Probando proxy a Auth Service...")
        with app.test_client() as client:
            response = client.get('/auth/health')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Auth Service Status: {data.get('status')}")
            else:
                print(f"   Error: {response.status_code}")
        
        # Probar proxy a User Service
        print("\n5️⃣ Probando proxy a User Service...")
        with app.test_client() as client:
            response = client.get('/user/health')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   User Service Status: {data.get('status')}")
            else:
                print(f"   Error: {response.status_code}")
        
        # Probar proxy a Task Service
        print("\n6️⃣ Probando proxy a Task Service...")
        with app.test_client() as client:
            response = client.get('/task/info')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Task Service: {data.get('service')}")
            else:
                print(f"   Error: {response.status_code}")
        
        print("\n🎉 Pruebas del API Gateway MongoDB completadas!")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_gateway()
