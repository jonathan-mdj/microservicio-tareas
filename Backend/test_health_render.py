# test_health_render.py - Probar el endpoint de health mejorado para Render
from api_gateway.app_mongo import app

def test_health_endpoint():
    """Probar el endpoint de health mejorado"""
    print("🏥 Probando endpoint de health mejorado para Render...")
    
    try:
        with app.test_client() as client:
            response = client.get('/health')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Status: {data.get('status')}")
                print(f"   Message: {data.get('message')}")
                print(f"   MongoDB: {data.get('mongodb')}")
                print(f"   Render Ready: {data.get('render_ready')}")
                
                # Verificar colecciones
                collections = data.get('collections', {})
                print(f"   Collections:")
                for collection, status in collections.items():
                    print(f"     - {collection}: {status}")
                
                # Verificar logs
                logs = data.get('logs', 'N/A')
                print(f"   Logs: {logs}")
                
                # Verificar environment
                env = data.get('environment', {})
                print(f"   Environment:")
                for key, value in env.items():
                    print(f"     - {key}: {value}")
                
                print("   ✅ Endpoint de health funcionando correctamente")
                return True
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.get_json()}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error probando health: {e}")
        return False

if __name__ == "__main__":
    print("🔍 PRUEBAS DEL ENDPOINT DE HEALTH MEJORADO")
    print("=" * 50)
    
    success = test_health_endpoint()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Health check mejorado funcionando correctamente")
        print("✅ Listo para Render")
    else:
        print("❌ Hay problemas con el health check")
    print("=" * 50)
