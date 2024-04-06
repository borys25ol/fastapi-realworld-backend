from fastapi import APIRouter

from conduit.api.schemas.requests.user import UserUpdateRequest
from conduit.api.schemas.responses.user import CurrentUserResponse, UpdatedUserResponse
from conduit.core.dependencies import DBSession, IUserAuthService, JWTToken

router = APIRouter()


@router.get("", response_model=CurrentUserResponse)
async def get_current_user(
    token: JWTToken, session: DBSession, user_auth_service: IUserAuthService
) -> CurrentUserResponse:
    """
    Return current user.
    """
    user_dto = await user_auth_service.get_current_user(session=session, token=token)
    return CurrentUserResponse.from_dto(dto=user_dto, token=token)


@router.put("", response_model=UpdatedUserResponse)
async def update_current_user(
    payload: UserUpdateRequest,
    token: JWTToken,
    session: DBSession,
    user_auth_service: IUserAuthService,
) -> UpdatedUserResponse:
    """
    Update current user.
    """
    current_user = await user_auth_service.get_current_user(
        session=session, token=token
    )
    updated_user_dto = await user_auth_service.update_user(
        session=session, current_user=current_user, user_to_update=payload.to_dto()
    )
    return UpdatedUserResponse.from_dto(dto=updated_user_dto, token=token)
