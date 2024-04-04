from conduit.core.config import get_app_settings
from conduit.core.settings.base import BaseAppSettings


class Container:
    """Dependency injector project container."""

    def __init__(self, settings: BaseAppSettings) -> None:
        self._settings = settings


container = Container(settings=get_app_settings())
