from pydantic_settings import BaseSettings, SettingsConfigDict
from authlib.integrations.starlette_client import OAuth


class Settings(BaseSettings):
    """
    Class to access env variables
    """
    mode: str

    db_url_sync: str
    db_url_test: str
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
    jwt_algorithm: str

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

    test: str

    celery_broker_url: str
    celery_broker_url_test: str
    celery_result_backend: str
    celery_result_backend_test: str

    model_config: SettingsConfigDict = {
        "env_file": ".env",
        "case_sensitive": False
    }

# Initialize settings
settings = Settings()  # noqa

social_oauth = OAuth()

social_oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url=settings.google_conf_url,
    client_kwargs={
        "scope": "openid email profile",
        "access_type": "offline"
    }
)

social_oauth.register(
    name="facebook",
    client_id=settings.facebook_client_id,
    client_secret=settings.facebook_client_secret,
    authorize_url='https://www.facebook.com/dialog/oauth',
    authorize_params=None,
    access_token_url='https://graph.facebook.com/v8.0/oauth/access_token',
    access_token_params=None,
    client_kwargs={'scope': 'email'},
    userinfo_endpoint='https://graph.facebook.com/me?fields=id,name,email'
)

social_oauth.register(
    name="github",
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={
        "scope": "profile user:email"
    }
)
