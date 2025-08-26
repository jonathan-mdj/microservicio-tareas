import re

def fix_task_service():
    print("🔧 Corrigiendo Task Service MongoDB...")
    
    try:
        # Leer el archivo
        with open('task_service/app_mongo.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar todas las ocurrencias de "admin" por "Profesor"
        content = content.replace('current_user = "admin"  # Simulado', 'current_user = "Profesor"  # Simulado')
        
        # Escribir el archivo corregido
        with open('task_service/app_mongo.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Task Service corregido exitosamente")
        print("   - Cambiado 'admin' por 'Profesor' en todas las funciones")
        
    except Exception as e:
        print(f"❌ Error corrigiendo Task Service: {e}")

if __name__ == "__main__":
    fix_task_service()
