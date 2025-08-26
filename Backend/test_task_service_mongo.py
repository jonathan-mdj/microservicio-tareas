from task_service.app_mongo import app
from database_mongo import mongo_db

def test_task_service():
    print("🧪 Probando Task Service MongoDB...")
    
    try:
        # Probar endpoint /health
        print("\n1️⃣ Probando endpoint /health...")
        with app.test_client() as client:
            response = client.get('/health')
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.get_json()}")
        
        # Probar endpoint /info
        print("\n2️⃣ Probando endpoint /info...")
        with app.test_client() as client:
            response = client.get('/info')
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   User: {data.get('user')}")
        
        # Probar endpoint /tasks (sin autorización)
        print("\n3️⃣ Probando endpoint /tasks (sin autorización)...")
        with app.test_client() as client:
            response = client.get('/tasks')
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            print(f"   Error: {data.get('error')}")
        
        # Probar endpoint /tasks (con autorización simulada)
        print("\n4️⃣ Probando endpoint /tasks (con autorización)...")
        with app.test_client() as client:
            response = client.get('/tasks', headers={'Authorization': 'Bearer dummy'})
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            if response.status_code == 200:
                print(f"   Tareas encontradas: {data.get('count', 0)}")
            else:
                print(f"   Error: {data.get('error')}")
        
        print("\n🎉 Pruebas del Task Service completadas!")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_task_service()
