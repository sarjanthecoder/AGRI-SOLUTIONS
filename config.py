import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/velgo_agri')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'velgo_admin_secret_key_12345')
    
    # JWT Configuration
    JWT_SECRET = os.getenv('JWT_SECRET', 'velgo_jwt_secret_key_12345')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    
    # Admin Defaults (for initial setup)
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@velgo.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 2592000  # 30 days in seconds
