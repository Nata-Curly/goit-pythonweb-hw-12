from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    This class definition is for a Settings class that inherits from BaseSettings. It defines a set of configuration settings for an application.
    The model_config attribute defines how the settings are loaded from environment variables and a .env file.
    """
    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: EmailStr 
    MAIL_PASSWORD: str 
    MAIL_FROM: EmailStr 
    MAIL_PORT: int 
    MAIL_SERVER: str 
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLD_NAME: str
    CLD_API_KEY: int 
    CLD_API_SECRET: str 

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
