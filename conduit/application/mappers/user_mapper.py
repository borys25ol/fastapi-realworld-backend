from conduit.application.dtos.user import (
    CreatedUserDTO,
    LoggedInUserDTO,
    UpdatedUserDTO,
    UserDTO,
)
from conduit.domain.entities.user import User


def entity_to_user_dto(user: User) -> UserDTO:
    dto = UserDTO(
        username=user.username,
        email=user.email,
        password_hash=user.password_hash,
        bio=user.bio,
        image_url=user.image_url or "",
        created_at=user.created_at,
    )
    dto.id = user.id
    return dto


def entity_to_created_user_dto(user: User, token: str) -> CreatedUserDTO:
    return CreatedUserDTO(
        id=user.id,
        email=user.email,
        username=user.username,
        bio=user.bio,
        image=user.image_url or "",
        token=token,
    )


def entity_to_logged_in_user_dto(user: User, token: str) -> LoggedInUserDTO:
    return LoggedInUserDTO(
        email=user.email,
        username=user.username,
        bio=user.bio,
        image=user.image_url or "",
        token=token,
    )


def user_dto_to_created_user_dto(user: UserDTO, token: str) -> CreatedUserDTO:
    return CreatedUserDTO(
        id=user.id,
        email=user.email,
        username=user.username,
        bio=user.bio,
        image=user.image_url,
        token=token,
    )


def user_dto_to_logged_in_user_dto(user: UserDTO, token: str) -> LoggedInUserDTO:
    return LoggedInUserDTO(
        email=user.email,
        username=user.username,
        bio=user.bio,
        image=user.image_url,
        token=token,
    )


def entity_to_updated_user_dto(user: User) -> UpdatedUserDTO:
    return UpdatedUserDTO(
        id=user.id,
        email=user.email,
        username=user.username,
        bio=user.bio,
        image=user.image_url or "",
    )
