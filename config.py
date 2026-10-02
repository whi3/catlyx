from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "CatalystCare API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    FIREBASE_CREDENTIALS: str = ""
    FIREBASE_PROJECT_ID: str = ""

    SMS_ENABLED: bool = False
    SMS_PROVIDER_URL: str = ""
    SMS_API_KEY: str = ""
    SMS_SENDER_ID: str = "CatalystX"

    # Keep decision support disabled until the current rules receive documented
    # approval from the local clinical governance team.
    RISK_RULES_CLINICALLY_APPROVED: bool = False
    NOTIFICATION_MAX_ATTEMPTS: int = 5

    model_config = SettingsConfigDict(env_file=".env")
        
settings = Settings()
