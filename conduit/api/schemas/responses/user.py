from pydantic import BaseModel

from conduit.domain.dtos.user import CreatedUserDTO, LoggedInUserDTO, UserDTO


class LoggedInUserData(BaseModel):
    email: str
    username: str
    bio: str
    image: str
    token: str


class RegisteredUserData(LoggedInUserData):
    id: int


class CurrentUserData(RegisteredUserData):
    pass


class UserRegistrationResponse(BaseModel):
    user: RegisteredUserData

    @classmethod
    def from_dto(cls, dto: CreatedUserDTO) -> "UserRegistrationResponse":
        return UserRegistrationResponse(
            user=RegisteredUserData(
                id=dto.id,
                email=dto.email,
                username=dto.username,
                bio=dto.bio,
                image=dto.image,
                token=dto.token,
            )
        )


class UserLoginResponse(BaseModel):
    user: LoggedInUserData

    @classmethod
    def from_dto(cls, dto: LoggedInUserDTO) -> "UserLoginResponse":
        return UserLoginResponse(
            user=LoggedInUserData(
                email=dto.email,
                username=dto.username,
                bio=dto.bio,
                image=dto.image,
                token=dto.token,
            )
        )


class CurrentUserResponse(BaseModel):
    user: CurrentUserData

    @classmethod
    def from_dto(cls, dto: UserDTO, token: str) -> "CurrentUserResponse":
        return CurrentUserResponse(
            user=CurrentUserData(
                id=dto.id,
                email=dto.email,
                username=dto.username,
                bio=dto.bio,
                image=dto.image_url,
                token=token,
            )
        )
