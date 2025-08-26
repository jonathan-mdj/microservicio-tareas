# migrate_to_atlas.py - Migrar datos de MongoDB local a MongoDB Atlas
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import bcrypt
import pyotp

# Cargar variables de entorno
load_dotenv('.env.atlas')

class AtlasMigrator:
    def __init__(self):
        # MongoDB Local
        self.local_uri = 'mongodb://localhost:27017/'
        self.local_db_name = 'task_management'
        
        # MongoDB Atlas
        self.atlas_uri = os.getenv('MONGO_URI_ATLAS')
        self.atlas_db_name = 'task_management'
        
        # Conexiones
        self.local_client = None
        self.atlas_client = None
        self.local_db = None
        self.atlas_db = None
    
    def connect_local(self):
        """Conectar a MongoDB local"""
        try:
            print("🔌 Conectando a MongoDB local...")
            self.local_client = MongoClient(self.local_uri)
            self.local_db = self.local_client[self.local_db_name]
            self.local_client.admin.command('ismaster')
            print("✅ Conexión a MongoDB local exitosa")
            return True
        except Exception as e:
            print(f"❌ Error conectando a MongoDB local: {e}")
            return False
    
    def connect_atlas(self):
        """Conectar a MongoDB Atlas"""
        try:
            print("🌐 Conectando a MongoDB Atlas...")
            self.atlas_client = MongoClient(self.atlas_uri)
            self.atlas_db = self.atlas_client[self.atlas_db_name]
            self.atlas_client.admin.command('ismaster')
            print("✅ Conexión a MongoDB Atlas exitosa")
            return True
        except Exception as e:
            print(f"❌ Error conectando a MongoDB Atlas: {e}")
            return False
    
    def migrate_users(self):
        """Migrar usuarios de local a Atlas"""
        try:
            print("\n👥 Migrando usuarios...")
            
            # Obtener usuarios de local
            local_users = list(self.local_db.users.find({}))
            print(f"   Usuarios encontrados en local: {len(local_users)}")
            
            # Migrar cada usuario
            migrated_count = 0
            for user in local_users:
                try:
                    # Verificar si el usuario ya existe en Atlas
                    existing_user = self.atlas_db.users.find_one({
                        "$or": [
                            {"username": user['username']},
                            {"email": user.get('email')}
                        ]
                    })
                    
                    if existing_user:
                        print(f"   ⚠️ Usuario {user['username']} ya existe en Atlas, saltando...")
                        continue
                    
                    # Preparar usuario para Atlas
                    atlas_user = {
                        "username": user['username'],
                        "email": user.get('email'),
                        "password": user['password'],
                        "role": user.get('role', 'user'),
                        "otp_secret": user.get('otp_secret'),
                        "require_otp": user.get('require_otp', True),
                        "created_at": user.get('created_at', datetime.utcnow())
                    }
                    
                    # Insertar en Atlas
                    result = self.atlas_db.users.insert_one(atlas_user)
                    print(f"   ✅ Usuario {user['username']} migrado (ID: {result.inserted_id})")
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Error migrando usuario {user['username']}: {e}")
            
            print(f"   🎉 Usuarios migrados exitosamente: {migrated_count}")
            return migrated_count
            
        except Exception as e:
            print(f"❌ Error en migración de usuarios: {e}")
            return 0
    
    def migrate_tasks(self):
        """Migrar tareas de local a Atlas"""
        try:
            print("\n📋 Migrando tareas...")
            
            # Obtener tareas de local
            local_tasks = list(self.local_db.tasks.find({"is_alive": True}))
            print(f"   Tareas encontradas en local: {len(local_tasks)}")
            
            # Migrar cada tarea
            migrated_count = 0
            for task in local_tasks:
                try:
                    # Verificar si la tarea ya existe en Atlas
                    existing_task = self.atlas_db.tasks.find_one({
                        "name": task['name'],
                        "created_by": task.get('created_by')
                    })
                    
                    if existing_task:
                        print(f"   ⚠️ Tarea '{task['name']}' ya existe en Atlas, saltando...")
                        continue
                    
                    # Preparar tarea para Atlas
                    atlas_task = {
                        "name": task['name'],
                        "description": task.get('description', ''),
                        "deadline": task.get('deadline'),
                        "status": task.get('status', 'In Progress'),
                        "created_by": task.get('created_by'),
                        "created_by_username": task.get('created_by_username'),
                        "created_at": task.get('created_at', datetime.utcnow()),
                        "is_alive": True
                    }
                    
                    # Insertar en Atlas
                    result = self.atlas_db.tasks.insert_one(atlas_task)
                    print(f"   ✅ Tarea '{task['name']}' migrada (ID: {result.inserted_id})")
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Error migrando tarea '{task['name']}': {e}")
            
            print(f"   🎉 Tareas migradas exitosamente: {migrated_count}")
            return migrated_count
            
        except Exception as e:
            print(f"❌ Error en migración de tareas: {e}")
            return 0
    
    def migrate_roles(self):
        """Migrar roles de local a Atlas"""
        try:
            print("\n🔐 Migrando roles...")
            
            # Obtener roles de local
            local_roles = list(self.local_db.roles.find({}))
            print(f"   Roles encontrados en local: {len(local_roles)}")
            
            # Migrar cada rol
            migrated_count = 0
            for role in local_roles:
                try:
                    # Verificar si el rol ya existe en Atlas
                    existing_role = self.atlas_db.roles.find_one({
                        "name": role['name']
                    })
                    
                    if existing_role:
                        print(f"   ⚠️ Rol '{role['name']}' ya existe en Atlas, saltando...")
                        continue
                    
                    # Preparar rol para Atlas
                    atlas_role = {
                        "name": role['name'],
                        "description": role.get('description', '')
                    }
                    
                    # Insertar en Atlas
                    result = self.atlas_db.roles.insert_one(atlas_role)
                    print(f"   ✅ Rol '{role['name']}' migrado (ID: {result.inserted_id})")
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Error migrando rol '{role['name']}': {e}")
            
            print(f"   🎉 Roles migrados exitosamente: {migrated_count}")
            return migrated_count
            
        except Exception as e:
            print(f"❌ Error en migración de roles: {e}")
            return 0
    
    def create_indices(self):
        """Crear índices en MongoDB Atlas"""
        try:
            print("\n📊 Creando índices en Atlas...")
            
            # Índices para usuarios
            self.atlas_db.users.create_index("username", unique=True)
            self.atlas_db.users.create_index("email", unique=True)
            print("   ✅ Índices de usuarios creados")
            
            # Índices para tareas
            self.atlas_db.tasks.create_index("created_by")
            self.atlas_db.tasks.create_index("status")
            self.atlas_db.tasks.create_index("created_at")
            print("   ✅ Índices de tareas creados")
            
            # Índices para roles
            self.atlas_db.roles.create_index("name", unique=True)
            print("   ✅ Índices de roles creados")
            
            print("   🎉 Todos los índices creados exitosamente")
            
        except Exception as e:
            print(f"❌ Error creando índices: {e}")
    
    def run_migration(self):
        """Ejecutar migración completa"""
        print("🚀 INICIANDO MIGRACIÓN A MONGODB ATLAS")
        print("=" * 50)
        
        # Conectar a ambas bases de datos
        if not self.connect_local():
            return False
        
        if not self.connect_atlas():
            return False
        
        try:
            # Migrar datos
            users_migrated = self.migrate_users()
            tasks_migrated = self.migrate_tasks()
            roles_migrated = self.migrate_roles()
            
            # Crear índices
            self.create_indices()
            
            print("\n" + "=" * 50)
            print("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 50)
            print(f"   👥 Usuarios migrados: {users_migrated}")
            print(f"   📋 Tareas migradas: {tasks_migrated}")
            print(f"   🔐 Roles migrados: {roles_migrated}")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            return False
        
        finally:
            # Cerrar conexiones
            if self.local_client:
                self.local_client.close()
            if self.atlas_client:
                self.atlas_client.close()
            print("\n🔌 Conexiones cerradas")

def main():
    """Función principal"""
    if not os.path.exists('.env.atlas'):
        print("❌ Archivo .env.atlas no encontrado")
        print("📝 Crea el archivo .env.atlas basándote en env_atlas_example.txt")
        return
    
    migrator = AtlasMigrator()
    success = migrator.run_migration()
    
    if success:
        print("\n✅ La migración se completó exitosamente")
        print("🌐 Ahora puedes usar MongoDB Atlas en producción")
    else:
        print("\n❌ La migración falló")
        print("🔍 Revisa los errores y verifica la configuración")

if __name__ == "__main__":
    main()
