from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    WP_DB_USER: str
    WP_DB_PASSWORD: str
    WP_DB_HOST: str
    WP_DB_PORT: int
    WP_DB_NAME: str

    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    APP_DEBUG: bool = True

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    INTRANET_SSO_SECRET: str
    INTRANET_SSO_EXPIRE_SECONDS: int = 120

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_USE_TLS: bool = True

    POINT_SALE_LOGIN_CODE_EXPIRE_MINUTES: int = 10
    POINT_SALE_LOGIN_MAX_ATTEMPTS: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()