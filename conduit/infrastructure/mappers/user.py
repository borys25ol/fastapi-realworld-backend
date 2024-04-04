from conduit.domain.dtos.user import UserDTO
from conduit.domain.mapper import IModelMapper
from conduit.infrastructure.models import User


class UserModelMapper(IModelMapper[User, UserDTO]):

    @staticmethod
    def to_dto(model: User) -> UserDTO:
        dto = UserDTO(
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            bio=model.bio,
            image_url=model.image_url,
            created_at=model.created_at,
        )
        dto.id = model.id
        return dto

    @staticmethod
    def from_dto(dto: UserDTO) -> User:
        model = User(
            username=dto.username,
            email=dto.email,
            bio=dto.bio,
            password_hash=dto.password_hash,
            image_url=dto.image_url,
            created_at=dto.created_at,
        )
        if hasattr(dto, "id"):
            model.id = dto.id
        return model
