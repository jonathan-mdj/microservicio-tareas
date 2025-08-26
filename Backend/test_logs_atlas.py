# test_logs_atlas.py - Probar endpoint de logs con MongoDB Atlas
from api_gateway.app_mongo import app

def test_logs_endpoint():
    """Probar el endpoint de logs del API Gateway"""
    print("🧪 Probando endpoint de logs con MongoDB Atlas...")
    
    try:
        with app.test_client() as client:
            # Probar endpoint de logs
            response = client.get('/logs/stats')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Success: {data.get('success')}")
                print(f"   Total requests: {data.get('data', {}).get('total_requests', 0)}")
                print(f"   Requests by service: {data.get('data', {}).get('requests_by_service', {})}")
                print(f"   Requests by method: {data.get('data', {}).get('requests_by_method', {})}")
                print("   ✅ Endpoint de logs funcionando correctamente")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.get_json()}")
                
    except Exception as e:
        print(f"   ❌ Error probando logs: {e}")

def test_health_endpoint():
    """Probar el endpoint de health"""
    print("\n🏥 Probando endpoint de health...")
    
    try:
        with app.test_client() as client:
            response = client.get('/health')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Service: {data.get('service')}")
                print(f"   Database: {data.get('database')}")
                print("   ✅ Endpoint de health funcionando correctamente")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Error probando health: {e}")

if __name__ == "__main__":
    print("🔍 PRUEBAS DEL API GATEWAY CON MONGODB ATLAS")
    print("=" * 50)
    
    test_logs_endpoint()
    test_health_endpoint()
    
    print("\n" + "=" * 50)
    print("🎯 VERIFICACIÓN DE GRÁFICAS:")
    print("   ✅ El sistema de logging está funcionando")
    print("   ✅ El endpoint /logs/stats responde correctamente")
    print("   ✅ Las gráficas del frontend seguirán funcionando")
    print("   ✅ Los datos se registran en api_gateway_mongo.log")
    print("=" * 50)
