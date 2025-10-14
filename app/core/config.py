"""
Application configuration.
"""


from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    """Application settings."""

    # API settings
    app_name: str = "Apple Store Parser API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # iTunes API settings
    itunes_timeout: int = 15
    itunes_user_agent: str = "storelytics/1.0"

    # Review collection settings
    default_review_limit: int = 300
    max_review_limit: int = 2000
    default_delay: float = 1.0

    # Text processing settings
    default_min_tokens: int = 3
    default_keep_emojis: bool = False
    default_lowercase: bool = True

    # Data storage
    data_dir: str = "data"

    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


# Global settings instance
settings = Settings()
