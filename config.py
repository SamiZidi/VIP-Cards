from datetime import timedelta
import os
import dotenv
dotenv.load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = int(os.getenv("port", 6543)) 
DBNAME = os.getenv("dbname")

class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,           # Maximum number of connections to keep open
        'max_overflow': 10,       # Additional connections when pool is full
        'pool_pre_ping': True,    # Verify connections before using
        'pool_recycle': 3600,     # Recycle connections after 1 hour
        'pool_timeout': 30        # Timeout for getting connection from pool
    }