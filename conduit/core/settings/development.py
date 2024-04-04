import logging

from conduit.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    """
    Development application settings.
    """

    debug: bool = True

    title: str = "[DEV] Conduit API"

    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = ".env.dev"
