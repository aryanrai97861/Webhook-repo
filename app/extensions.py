from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB extension
# Configure with: MONGO_URI in .env file
# Example: mongodb+srv://username:password@cluster.mongodb.net/github_events

class MongoDBExtension:
    """Custom MongoDB extension for Flask"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
    
    def init_app(self, app):
        """Initialize MongoDB connection with Flask app"""
        from pymongo import MongoClient
        
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        database_name = os.getenv('DATABASE_NAME', 'github_events')
        collection_name = os.getenv('COLLECTION_NAME', 'events')
        
        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully!")
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            self.collection = None


# Initialize the extension
mongo = MongoDBExtension()
