from pydantic import BaseModel

from conduit.domain.dtos.tag import TagDTO


class TagsResponse(BaseModel):
    tags: list[str]

    @classmethod
    def from_dtos(cls, dtos: list[TagDTO]) -> "TagsResponse":
        return TagsResponse(tags=[dto.tag for dto in dtos])
