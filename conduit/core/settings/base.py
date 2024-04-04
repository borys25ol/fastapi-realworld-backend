from pydantic import Extra
from pydantic_settings import BaseSettings


class AppEnvTypes:
    """
    Available application environments.
    """

    production = "prod"
    development = "dev"
    testing = "test"


class BaseAppSettings(BaseSettings):
    """
    Base application setting class.
    """

    app_env: str = AppEnvTypes.production

    class Config:
        env_file = ".env"
        extra = Extra.ignore
