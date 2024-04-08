from pydantic import BaseModel

from conduit.domain.dtos.profile import ProfileDTO


class ProfileData(BaseModel):
    username: str
    bio: str | None
    image: str | None
    following: bool


class ProfileResponse(BaseModel):
    profile: ProfileData

    @classmethod
    def from_dto(cls, dto: ProfileDTO) -> "ProfileResponse":
        return ProfileResponse(
            profile=ProfileData(
                username=dto.username,
                bio=dto.bio,
                image=dto.image,
                following=dto.following,
            )
        )
