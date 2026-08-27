from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Solar Power Prediction API"
    PROJECT_START_DATE: datetime = datetime(2026, 1, 1)
    
    # Database Configuration
    DB_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "solar_prediction.db")
    SQLALCHEMY_DATABASE_URL: str = f"sqlite:///{DB_PATH}"

    # Weather API (if any, as fallback)
    OPEN_METEO_URL: str = "https://archive-api.open-meteo.com/v1/archive"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()
