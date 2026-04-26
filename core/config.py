from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Stripe Auth
    STRIPE_RESTRICTED_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0" # Update for Render Redis
    
    # GHL & Email (Placeholders for now)
    GHL_ACCESS_TOKEN: str = ""
    GHL_LOCATION_ID: str = ""
    EMAIL_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()