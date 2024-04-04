from abc import ABC, abstractmethod
from typing import Generic, TypeVar

M_ = TypeVar("M_")
D_ = TypeVar("D_")


class IModelMapper(ABC, Generic[M_, D_]):
    """Interface for model mapping."""

    @staticmethod
    @abstractmethod
    def to_dto(model: M_) -> D_: ...

    @staticmethod
    @abstractmethod
    def from_dto(dto: D_) -> M_: ...
