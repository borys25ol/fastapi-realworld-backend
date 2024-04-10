import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class TagDTO:
    id: int
    tag: str
    created_at: datetime.datetime
