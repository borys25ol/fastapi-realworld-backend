from fastapi import APIRouter

from conduit.api.schemas.requests.user import UserUpdateRequest
from conduit.api.schemas.responses.user import CurrentUserResponse, UpdatedUserResponse
from conduit.core.dependencies import CurrentUser, DBSession, IUserService, JWTToken

router = APIRouter()


@router.get("", response_model=CurrentUserResponse)
async def get_current_user(
    token: JWTToken, current_user: CurrentUser
) -> CurrentUserResponse:
    """
    Return current user.
    """
    return CurrentUserResponse.from_dto(dto=current_user, token=token)


@router.put("", response_model=UpdatedUserResponse)
async def update_current_user(
    payload: UserUpdateRequest,
    token: JWTToken,
    session: DBSession,
    current_user: CurrentUser,
    user_service: IUserService,
) -> UpdatedUserResponse:
    """
    Update current user.
    """
    updated_user_dto = await user_service.update_user(
        session=session, current_user=current_user, user_to_update=payload.to_dto()
    )
    return UpdatedUserResponse.from_dto(dto=updated_user_dto, token=token)
