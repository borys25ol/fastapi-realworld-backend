from fastapi import APIRouter

from conduit.api.mappers.user_mapper import (
    request_to_create_user_dto,
    request_to_login_user_dto,
)
from conduit.api.schemas.requests.user import UserLoginRequest, UserRegistrationRequest
from conduit.api.schemas.responses.user import (
    UserLoginResponse,
    UserRegistrationResponse,
)
from conduit.core.dependencies import IUserAuthService, UnitOfWork

router = APIRouter()


@router.post("", response_model=UserRegistrationResponse)
async def register_user(
    payload: UserRegistrationRequest,
    uow: UnitOfWork,
    user_auth_service: IUserAuthService,
) -> UserRegistrationResponse:
    """
    Process user registration.
    """
    user_dto = await user_auth_service.sign_up_user(
        uow=uow, user_to_create=request_to_create_user_dto(payload)
    )
    return UserRegistrationResponse.from_dto(dto=user_dto)


@router.post("/login", response_model=UserLoginResponse)
async def login_user(
    payload: UserLoginRequest, uow: UnitOfWork, user_auth_service: IUserAuthService
) -> UserLoginResponse:
    """
    Process user login.
    """
    user_dto = await user_auth_service.sign_in_user(
        uow=uow, user_to_login=request_to_login_user_dto(payload)
    )
    return UserLoginResponse.from_dto(dto=user_dto)
