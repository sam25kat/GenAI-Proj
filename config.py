import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""

    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'

    # FAISS
    FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', './faiss_index.bin')
    FAISS_METADATA_PATH = os.getenv('FAISS_METADATA_PATH', './faiss_metadata.json')

    # Embedding Model
    EMBEDDING_MODEL = "text-embedding-3-large"
    EMBEDDING_DIMENSION = 3072

    # LLM Model
    LLM_MODEL = "gpt-4o-mini"

    # FAISS Search
    SIMILAR_QUERIES_LIMIT = 3
