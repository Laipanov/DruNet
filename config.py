from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./auth.db"

    # JWT
    JWT_SECRET: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # MSG OVRX API
    MSG_OVRX_API_KEY: str = "your-msg-ovrx-api-key"
    MSG_OVRX_BASE_URL: str = "https://api.msgovrx.ru"
    SMS_SENDER_NAME: str = "YourApp"

    class Config:
        env_file = ".env"


settings = Settings()