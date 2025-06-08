from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Class to access env variables
    """

    mode: str

    port: str

    db_url_sync: str
    db_url_test: str
    db_url_async: str
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_schema: str

    jwt_access_token_expiry: int
    jwt_refresh_token_expiry: int
    jwt_algorithm: str
    secrets: str
    jwt_secrets: str
    jwt_algorithm: str
    jwt_issuer: str
    jwt_audience: str

    mail_port: int
    mail_username: str
    mail_password: str
    mail_server: str

    frontend_url: str

    google_client_id: str
    google_client_secret: str
    google_conf_url: str

    github_client_id: str
    github_client_secret: str

    facebook_client_id: str
    facebook_client_secret: str

    celery_broker_url: str
    celery_broker_url_test: str
    celery_result_backend: str
    celery_result_backend_test: str

    redis_url: str

    model_config: SettingsConfigDict = {  # type: ignore
        "env_file": ".env",
        "case_sensitive": False,
    }


# Initialize settings
settings = Settings()  # type: ignore
