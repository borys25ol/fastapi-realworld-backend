from conduit.application.dtos.profile import ProfileDTO
from conduit.application.dtos.user import UserDTO


def user_to_profile_dto(user: UserDTO, following: bool) -> ProfileDTO:
    return ProfileDTO(
        user_id=user.id,
        username=user.username,
        bio=user.bio,
        image=user.image_url,
        following=following,
    )
