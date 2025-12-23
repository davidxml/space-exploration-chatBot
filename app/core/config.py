import os
from dotenv import load_dotenv

# Load .env file from the root directory
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Royce: Space Exploration ChatBot"
    VERSION: str = "1.1.0"
    
    # API Config
    API_V1_STR: str = "/api/v1"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Secrets
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    VECTOR_DB_PATH = os.path.join(BASE_DIR, "../data/vector_store")
    RAW_DATA_PATH = os.path.join(BASE_DIR, "../data/raw")

    # Model Config
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_MODEL: str = "llama-3.3-70b-versatile"

# Singleton instance
settings = Settings()

if not settings.GROQ_API_KEY:
    print("⚠️ WARNING: GROQ_API_KEY not found in environment variables!")