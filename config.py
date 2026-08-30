from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    FIREBASE_CREDENTIALS: str

    SMS_ENABLED: bool = False
    SMS_PROVIDER_URL: str = ""
    SMS_API_KEY: str = ""
    SMS_SENDER_ID: str = "CatalystX"

    class Config:
        env_file = ".env"
        
settings = Settings()