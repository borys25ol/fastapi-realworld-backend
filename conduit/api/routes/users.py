from fastapi import APIRouter

from conduit.api.schemas.requests.user import (
    UserLoginRequest,
    UserRegistrationRequest,
    UserUpdateRequest,
)
from conduit.api.schemas.responses.user import (
    CurrentUserResponse,
    UserLoginResponse,
    UserRegistrationResponse,
)
from conduit.core.dependencies import DBSession, IUserAuthService, JWTToken

router = APIRouter()


@router.get("/user", response_model=CurrentUserResponse)
async def get_current_user(
    token: JWTToken, session: DBSession, user_auth_service: IUserAuthService
) -> CurrentUserResponse:
    """
    Return current user.
    """
    dto = await user_auth_service.get_current_user(session=session, token=token)
    return CurrentUserResponse.from_dto(dto=dto, token=token)


@router.put("/user", response_model=CurrentUserResponse)
async def update_current_user(
    payload: UserUpdateRequest,
    token: JWTToken,
    session: DBSession,
    user_auth_service: IUserAuthService,
) -> CurrentUserResponse:
    """
    Update current user.
    """
    current_user = await user_auth_service.get_current_user(
        session=session, token=token
    )
    dto = await user_auth_service.update_user(
        session=session, user_id=current_user.id, user_to_update=payload.to_dto()
    )
    return CurrentUserResponse.from_dto(dto=dto, token=token)


@router.post("/users", response_model=UserRegistrationResponse)
async def register_user(
    payload: UserRegistrationRequest,
    session: DBSession,
    user_auth_service: IUserAuthService,
) -> UserRegistrationResponse:
    """
    Process user registration.
    """
    dto = await user_auth_service.sign_up_user(
        session=session, user_to_create=payload.to_dto()
    )
    return UserRegistrationResponse.from_dto(dto=dto)


@router.post("/users/login", response_model=UserLoginResponse)
async def login_user(
    payload: UserLoginRequest, session: DBSession, user_auth_service: IUserAuthService
) -> UserLoginResponse:
    """
    Process user login.
    """
    dto = await user_auth_service.sign_in_user(
        session=session, user_to_login=payload.to_dto()
    )
    return UserLoginResponse.from_dto(dto=dto)
