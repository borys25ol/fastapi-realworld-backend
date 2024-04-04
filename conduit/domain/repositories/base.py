import abc
from typing import Any, Generic, TypeVar

from conduit.domain.specifications import ISpecification

_DTO = TypeVar("_DTO")
_ID = TypeVar("_ID")


class ICRUDRepository(abc.ABC, Generic[_ID, _DTO]):
    """CRUD repository interface."""

    @abc.abstractmethod
    async def get_all(
        self, session: Any, specification: ISpecification | None = ...
    ) -> list[_DTO]: ...

    @abc.abstractmethod
    async def get_by_id(self, session: Any, item_id: _ID) -> _DTO: ...

    @abc.abstractmethod
    async def create(self, session: Any, item: _DTO) -> _ID: ...

    @abc.abstractmethod
    async def update(self, session: Any, item: _DTO) -> _ID: ...

    @abc.abstractmethod
    async def delete(self, session: Any, item_id: _ID) -> None: ...
