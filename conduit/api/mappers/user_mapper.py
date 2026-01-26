from conduit.api.schemas.requests.user import (
    UserLoginRequest,
    UserRegistrationRequest,
    UserUpdateRequest,
)
from conduit.application.dtos.user import CreateUserDTO, LoginUserDTO, UpdateUserDTO


def request_to_create_user_dto(request: UserRegistrationRequest) -> CreateUserDTO:
    return CreateUserDTO(
        username=request.user.username,
        email=request.user.email,
        password=request.user.password,
    )


def request_to_login_user_dto(request: UserLoginRequest) -> LoginUserDTO:
    return LoginUserDTO(email=request.user.email, password=request.user.password)


def request_to_update_user_dto(request: UserUpdateRequest) -> UpdateUserDTO:
    return UpdateUserDTO(
        email=request.user.email,
        password=request.user.password,
        username=request.user.username,
        bio=request.user.bio,
        image_url=request.user.image,
    )
