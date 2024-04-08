from fastapi import APIRouter

from conduit.api.schemas.responses.profile import ProfileResponse
from conduit.core.dependencies import (
    CurrentOptionalUser,
    CurrentUser,
    DBSession,
    IProfileService,
)

router = APIRouter()


@router.get("/{username}", response_model=ProfileResponse)
async def get_user_profile(
    username: str,
    session: DBSession,
    current_user: CurrentOptionalUser,
    profile_service: IProfileService,
) -> ProfileResponse:
    """
    Return user profile information.
    """
    profile_dto = await profile_service.get_profile_by_username(
        session=session, username=username, current_user=current_user
    )
    return ProfileResponse.from_dto(dto=profile_dto)


@router.post("/{username}/follow", response_model=ProfileResponse)
async def follow_username(
    username: str,
    session: DBSession,
    current_user: CurrentUser,
    profile_service: IProfileService,
) -> ProfileResponse:
    """
    Follow username profile.
    """
    await profile_service.add_user_into_followers(
        session=session, username=username, current_user=current_user
    )
    profile_dto = await profile_service.get_profile_by_username(
        session=session, username=username, current_user=current_user
    )
    return ProfileResponse.from_dto(dto=profile_dto)


@router.delete("/{username}/follow", response_model=ProfileResponse)
async def unfollow_username(
    username: str,
    session: DBSession,
    current_user: CurrentUser,
    profile_service: IProfileService,
) -> ProfileResponse:
    """
    Unfollow username profile.
    """
    await profile_service.remove_user_from_followers(
        session=session, username=username, current_user=current_user
    )
    profile_dto = await profile_service.get_profile_by_username(
        session=session, username=username, current_user=current_user
    )
    return ProfileResponse.from_dto(dto=profile_dto)
