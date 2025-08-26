from task_service.app_mongo import app

def test_task_creation():
    print("🧪 Probando creación de tareas en Task Service MongoDB...")
    
    try:
        # Probar creación de tarea nueva
        print("\n1️⃣ Probando creación de tarea nueva...")
        with app.test_client() as client:
            task_data = {
                "name": "Tarea de prueba MongoDB",
                "description": "Esta es una tarea de prueba para verificar el Task Service MongoDB",
                "deadline": "2025-12-31 23:59:59",
                "status": "In Progress"
            }
            response = client.post('/task', json=task_data, headers={'Authorization': 'Bearer dummy'})
            print(f"   Status: {response.status_code}")
            data = response.get_json()
            if response.status_code == 201:
                print(f"   ✅ Tarea creada exitosamente")
                print(f"   Task ID: {data.get('task', {}).get('id')}")
                print(f"   Name: {data.get('task', {}).get('name')}")
                print(f"   Status: {data.get('task', {}).get('status')}")
                print(f"   Deadline: {data.get('task', {}).get('deadline')}")
            else:
                print(f"   ❌ Error en creación: {data.get('error')}")
        
        # Verificar que la tarea se creó
        print("\n2️⃣ Verificando tarea creada...")
        with app.test_client() as client:
            response = client.get('/tasks', headers={'Authorization': 'Bearer dummy'})
            data = response.get_json()
            print(f"   Total tareas: {data.get('count', 0)}")
            if data.get('tasks'):
                for task in data['tasks']:
                    if task['name'] == 'Tarea de prueba MongoDB':
                        print(f"   ✅ Tarea 'Tarea de prueba MongoDB' encontrada en la lista")
                        print(f"   ID: {task['id']}")
                        print(f"   Status: {task['status']}")
                        break
                else:
                    print(f"   ❌ Tarea 'Tarea de prueba MongoDB' no encontrada en la lista")
        
        print("\n🎉 Pruebas de creación de tareas completadas!")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_task_creation()
