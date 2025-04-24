from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import logging
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "CounselAI-Pro"
    admin_email: str = "admin@example.com"
    google_genai_api_key: str = None  # Add this line
    items_per_user: int = 50
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    jwt_secret: str = os.getenv("JWT_SECRET", "super-secret-jwt-key")
    pii_encryption_key: str = os.getenv("PII_ENCRYPTION_KEY", "sixteen byte key")
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./test.db"
    )  # SQLite default for local dev
    model_path: str = os.getenv("MODEL_PATH", "/models")
    feature_flag_semantic_search: bool = os.getenv(
        "FEATURE_FLAG_SEMANTIC_SEARCH", "false"
    ).lower() == "true"
    feature_flag_advanced_risk: bool = os.getenv(
        "FEATURE_FLAG_ADVANCED_RISK", "false"
    ).lower() == "true"
    feature_flag_pii_detection: bool = os.getenv(
        "FEATURE_FLAG_PII_DETECTION", "true"
    ).lower() == "true"
    enable_encryption: bool = os.getenv("ENABLE_ENCRYPTION", "false").lower() == "true"
    allowed_origins: list = ["*"]  # Configure CORS carefully in production

    model_config = {
        "extra": "allow",  # To handle extra fields 
        "protected_namespaces": ('settings_',),  # To resolve model_path warning
        "env_file": ".env"  # This is how you specify env file in v2
    }

    DATABASE_URL: str = "sqlite:///./app.db"

@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

# Configure Logging (after settings are loaded)
logging.basicConfig(level=settings.log_level, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
