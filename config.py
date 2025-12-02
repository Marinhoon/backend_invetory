import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

class Config:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/inventory_control')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'inventory_control')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
