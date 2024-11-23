import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.api.schemas.responses.profile import ProfileResponse
from conduit.domain.dtos.user import UserDTO
from conduit.infrastructure.repositories.user import UserRepository
from tests.utils import create_another_test_user


@pytest.mark.anyio
async def test_not_authenticated_user_can_get_profile(
    test_client: AsyncClient, test_user: UserDTO
) -> None:
    response = await test_client.get(url=f"/profiles/{test_user.username}")
    profile = ProfileResponse(**response.json())
    assert profile.profile.username == test_user.username
    assert not profile.profile.following


@pytest.mark.anyio
async def test_authenticated_user_can_get_own_profile(
    authorized_test_client: AsyncClient, test_user: UserDTO
) -> None:
    response = await authorized_test_client.get(url=f"/profiles/{test_user.username}")
    profile = ProfileResponse(**response.json())
    assert profile.profile.username == test_user.username
    assert not profile.profile.following


@pytest.mark.anyio
async def test_not_authenticated_user_can_not_follow_another_user_profile(
    test_client: AsyncClient, test_user: UserDTO
) -> None:
    response = await test_client.post(url=f"/profiles/{test_user.username}/follow")
    assert response.status_code == 403


@pytest.mark.anyio
async def test_authenticated_user_cant_follow_own_profile(
    authorized_test_client: AsyncClient, test_user: UserDTO
) -> None:
    response = await authorized_test_client.post(
        url=f"/profiles/{test_user.username}/follow"
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_authenticated_user_cant_follow_another_profile(
    authorized_test_client: AsyncClient,
    test_user: UserDTO,
    user_repository: UserRepository,
    session: AsyncSession,
) -> None:
    new_user = await create_another_test_user(
        session=session, user_repository=user_repository
    )
    response = await authorized_test_client.post(
        url=f"/profiles/{new_user.username}/follow"
    )
    assert response.status_code == 200
    assert response.json()["profile"]["following"] is True


@pytest.mark.anyio
async def test_authenticated_user_cant_follow_already_followed_profile(
    authorized_test_client: AsyncClient,
    test_user: UserDTO,
    user_repository: UserRepository,
    session: AsyncSession,
) -> None:
    new_user = await create_another_test_user(
        session=session, user_repository=user_repository
    )
    response = await authorized_test_client.post(
        url=f"/profiles/{new_user.username}/follow"
    )
    assert response.status_code == 200
    assert response.json()["profile"]["following"] is True

    response = await authorized_test_client.post(
        url=f"/profiles/{new_user.username}/follow"
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_authenticated_user_cant_unfollow_not_followed_profile(
    authorized_test_client: AsyncClient,
    user_repository: UserRepository,
    session: AsyncSession,
) -> None:
    new_user = await create_another_test_user(
        session=session, user_repository=user_repository
    )
    response = await authorized_test_client.delete(
        url=f"/profiles/{new_user.username}/follow"
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_authenticated_user_can_unfollow_followed_profile(
    authorized_test_client: AsyncClient,
    user_repository: UserRepository,
    session: AsyncSession,
) -> None:
    new_user = await create_another_test_user(
        session=session, user_repository=user_repository
    )
    response = await authorized_test_client.post(
        url=f"/profiles/{new_user.username}/follow"
    )
    assert response.status_code == 200
    assert response.json()["profile"]["following"] is True

    response = await authorized_test_client.delete(
        url=f"/profiles/{new_user.username}/follow"
    )
    assert response.status_code == 200
    assert response.json()["profile"]["following"] is False


@pytest.mark.anyio
async def test_authenticated_user_can_unfollow_already_unfollowed_profile(
    authorized_test_client: AsyncClient,
    user_repository: UserRepository,
    session: AsyncSession,
) -> None:
    new_user = await create_another_test_user(
        session=session, user_repository=user_repository
    )
    response = await authorized_test_client.post(
        url=f"/profiles/{new_user.username}/follow"
    )
    assert response.status_code == 200
    assert response.json()["profile"]["following"] is True

    response = await authorized_test_client.delete(
        url=f"/profiles/{new_user.username}/follow"
    )
    assert response.status_code == 200
    assert response.json()["profile"]["following"] is False

    response = await authorized_test_client.delete(
        url=f"/profiles/{new_user.username}/follow"
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    "api_method, api_path",
    (
        ("GET", "/profiles/{username}"),
        ("POST", "/profiles/{username}/follow"),
        ("DELETE", "/profiles/{username}/follow"),
    ),
)
@pytest.mark.anyio
async def test_user_can_not_retrieve_not_existing_profile(
    authorized_test_client: AsyncClient, api_method: str, api_path: str
) -> None:
    response = await authorized_test_client.request(
        method=api_method, url=api_path.format(username="not-existing-username")
    )
    assert response.status_code == 404
