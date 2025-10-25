from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "sqlite:///./bus_booking.db"

    # JWT Authentication
    SECRET_KEY: str = (
        "your-secret-key-change-this-in-production-use-openssl-rand-hex-32"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    # Application
    APP_NAME: str = "Bus AgentUB API"
    DEBUG: bool = True

    # CORS (for frontend)
    CORS_ORIGINS: list = [
        "http://localhost:3000", 
        "http://localhost:8080",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080", 
        "http://127.0.0.1:5000",
        "*"  # Allow all origins for development
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
