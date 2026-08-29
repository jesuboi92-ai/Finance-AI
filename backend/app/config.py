from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Logistics SaaS"
    DEBUG: bool = True
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/logistics_saas"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://logistics-saas.azurewebsites.net"
    ]
    
    # Azure
    AZURE_CONNECTION_STRING: str = os.getenv("AZURE_CONNECTION_STRING", "")
    AZURE_STORAGE_CONTAINER: str = "logistics-files"
    
    # SendGrid
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SENDGRID_FROM_EMAIL: str = os.getenv("SENDGRID_FROM_EMAIL", "noreply@logistics-saas.com")
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Google Maps
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_DB: int = 0
    
    # OAuth2
    OAUTH2_GOOGLE_CLIENT_ID: str = os.getenv("OAUTH2_GOOGLE_CLIENT_ID", "")
    OAUTH2_GOOGLE_CLIENT_SECRET: str = os.getenv("OAUTH2_GOOGLE_CLIENT_SECRET", "")
    OAUTH2_MICROSOFT_CLIENT_ID: str = os.getenv("OAUTH2_MICROSOFT_CLIENT_ID", "")
    OAUTH2_MICROSOFT_CLIENT_SECRET: str = os.getenv("OAUTH2_MICROSOFT_CLIENT_SECRET", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
