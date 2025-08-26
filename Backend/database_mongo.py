from pymongo import MongoClient
from config import config

class MongoDB:
    def __init__(self):
        self.connection_string = config.MONGO_URI
        self.db_name = config.MONGO_DB_NAME
        self.client = None
        self.db = None
        
    def connect(self):
        try:
            if not self.connection_string or self.connection_string == 'mongodb://localhost:27017/':
                print("⚠️ Usando MongoDB local para desarrollo")
                # Configuración local para desarrollo
                self.client = MongoClient('mongodb://localhost:27017/')
                self.db = self.client[self.db_name]
            else:
                print("🌐 Conectando a MongoDB Atlas")
                self.client = MongoClient(self.connection_string)
                self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ismaster')
            print("✅ MongoDB connection successful!")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            return False
    
    def get_collection(self, collection_name):
        if self.db is None:
            self.connect()
        return self.db[collection_name]
    
    def close(self):
        if self.client:
            self.client.close()

# Singleton instance
mongo_db = MongoDB()
