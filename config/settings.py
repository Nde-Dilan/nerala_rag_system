import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # API settings
    API_VERSION = 'v1'
    
    # Gemini API settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
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