import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'sua-chave-secreta')
    JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-chave-secreta')
    JWT_EXPIRATION = timedelta(hours=24)
    
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '123456'),
        'database': os.getenv('DB_NAME', 'syp_ecommerce')
    }
    
    PORT = int(os.getenv('PORT', 5000))