import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

class Settings:
    """Configures project settings, reading from environment variables with fallbacks."""
    
    TEST_ENV: str = os.getenv("TEST_ENV", "local")
    
    # Target URL. 
    # (Note: In tests, the server port will be dynamically determined and updated, 
    # but for external runs/standalone testing this defaults to http://127.0.0.1:8000)
    BASE_URL: str = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    
    # Request timeout in seconds
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "5"))
    
    # Database path
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "inventory.db")
    
    # Log Level
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Singleton instance
settings = Settings()
