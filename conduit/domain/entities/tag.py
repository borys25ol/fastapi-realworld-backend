"""Domain entity for tags."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Tag:
    id: int
    tag: str
    created_at: datetime

    def rename(self, tag: str) -> None:
        self._validate_tag(tag)
        self.tag = tag

    @staticmethod
    def _validate_tag(value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Invalid tag")
