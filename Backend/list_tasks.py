from database_mongo import mongo_db

def list_tasks():
    print("📋 Listando todas las tareas en MongoDB...")
    
    try:
        mongo_db.connect()
        tasks_collection = mongo_db.get_collection('tasks')
        
        # Obtener todas las tareas
        tasks = list(tasks_collection.find({"is_alive": True}))
        
        print(f"\n📊 Total de tareas: {len(tasks)}")
        
        for i, task in enumerate(tasks, 1):
            print(f"\n{i}. Tarea:")
            print(f"   ID: {task['_id']}")
            print(f"   Name: {task['name']}")
            print(f"   Description: {task.get('description', 'N/A')}")
            print(f"   Status: {task.get('status', 'N/A')}")
            print(f"   Deadline: {task.get('deadline', 'N/A')}")
            print(f"   Created by: {task.get('created_by_username', 'N/A')}")
            print(f"   Created at: {task.get('created_at', 'N/A')}")
        
        print("\n🎉 Listado completado!")
        
    except Exception as e:
        print(f"❌ Error listando tareas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_tasks()
