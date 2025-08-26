from pymongo import MongoClient
import os

class MongoDBRender:
    def __init__(self):
        # En Render, usar variables de entorno directamente
        self.connection_string = os.getenv('MONGO_URI_ATLAS', '')
        self.db_name = 'task_management'
        self.client = None
        self.db = None
        
    def connect(self):
        try:
            if not self.connection_string:
                print("❌ MONGO_URI_ATLAS no configurada en variables de entorno")
                return False
            
            print("🌐 Conectando a MongoDB Atlas desde Render...")
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ismaster')
            print("✅ MongoDB Atlas connection successful!")
            return True
            
        except Exception as e:
            print(f"❌ MongoDB Atlas connection error: {e}")
            return False
    
    def get_collection(self, collection_name):
        if self.db is None:
            self.connect()
        return self.db[collection_name]
    
    def close(self):
        if self.client:
            self.client.close()

# Singleton instance para Render
mongo_db = MongoDBRender()
