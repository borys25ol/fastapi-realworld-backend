from pydantic import Extra, computed_field
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

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str

    class Config:
        env_file = ".env"
        extra = Extra.ignore

    @property
    @computed_field
    def sql_db_uri(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
