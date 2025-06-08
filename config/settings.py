import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # API settings
    API_VERSION = 'v1'
    
    # Gemini API settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
    
    # RAG settings
    DEFAULT_TOP_K = 3
    MAX_TOP_K = 10
    SUPPORTED_LANGUAGES = ['fulfulde', 'ghomala', 'english', 'french']
    
    # File paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    VECTOR_STORES_DIR = os.path.join(DATA_DIR, 'vector_stores')
    
    # Embedding settings
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    EMBEDDING_DIMENSION = 384
    
    # Security settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    REQUEST_TIMEOUT = 30  # seconds
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:*,http://127.0.0.1:*').split(',')
    
    # Hugging Face settings
    HF_REPO_ID = os.getenv('HF_REPO_ID', 'nde-dilan/nerala-rag-model')
    HF_TOKEN = os.getenv('HF_TOKEN')  # Optional for private repos
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    @staticmethod
    def validate_config():
        """Validate critical configuration"""
        required_vars = ['GEMINI_API_KEY']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    CORS_ORIGINS = ['http://localhost:*', 'http://127.0.0.1:*']

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Stricter CORS in production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    
    # Enhanced security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}