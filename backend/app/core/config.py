from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    Class to access env variables
    """
    db_url: str
    db_url_async: str
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_schema: str

    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int
    jwt_algorithm: str
    secrets: str

    mail_port: int
    mail_username: str
    mail_password: str

    frontend_url: str

    google_client_id: str
    google_client_secret: str

    test: str

    model_config: SettingsConfigDict = {
        "env_file": ".env",
        "case_sensitive": False
    }

# Initialize settings
settings = Settings()  # noqa
