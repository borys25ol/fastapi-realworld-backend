import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.domain.dtos.user import UserDTO
from conduit.infrastructure.repositories.user import UserRepository
from conduit.services.password import verify_password


@pytest.mark.anyio
async def test_failed_login_with_invalid_token_prefix(
    test_client: AsyncClient, test_user: UserDTO, jwt_token: str
) -> None:
    response = await test_client.get(
        url="/user", headers={"Authorization": f"JWTToken {jwt_token}"}
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_failed_login_when_user_does_not_exist(
    test_client: AsyncClient, not_exists_jwt_token: str
) -> None:
    response = await test_client.get(
        url="/user", headers={"Authorization": f"Token {not_exists_jwt_token}"}
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_user_can_not_get_profile_without_auth(
    test_client: AsyncClient, test_user: UserDTO
) -> None:
    response = await test_client.get(url="/user")
    assert response.status_code == 403


@pytest.mark.anyio
async def test_user_can_get_own_profile(
    authorized_test_client: AsyncClient, jwt_token: str
) -> None:
    response = await authorized_test_client.get(url="/user")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "update_field, update_value",
    (
        ("username", "updated_username"),
        ("email", "updated_email@gmail.com"),
        ("bio", "Updated bio"),
        ("image", "https://image.com/best-image-ever"),
    ),
)
@pytest.mark.anyio
async def test_user_can_update_own_profile(
    authorized_test_client: AsyncClient,
    test_user: UserDTO,
    update_value: str,
    update_field: str,
) -> None:
    response = await authorized_test_client.put(
        url="/user", json={"user": {update_field: update_value}}
    )
    assert response.status_code == 200

    updated_user = response.json()
    assert updated_user["user"][update_field] == update_value


@pytest.mark.anyio
async def test_user_can_change_password(
    authorized_test_client: AsyncClient,
    test_user: UserDTO,
    session: AsyncSession,
    user_repository: UserRepository,
) -> None:
    response = await authorized_test_client.put(
        url="/user", json={"user": {"password": "new_password"}}
    )
    assert response.status_code == 200

    user = await user_repository.get_by_email(session=session, email=test_user.email)
    assert verify_password(
        plain_password="new_password", hashed_password=user.password_hash
    )


@pytest.mark.parametrize(
    "update_field, update_value",
    (("username", "taken_username"), ("email", "taken@gmail.com")),
)
@pytest.mark.anyio
async def test_user_can_not_use_taken_credentials(
    authorized_test_client: AsyncClient, update_field: str, update_value: str
) -> None:
    payload = {
        "user": {
            "username": "free_username",
            "password": "password",
            "email": "free_email@gmail.com",
        }
    }
    payload["user"].update({update_field: update_value})
    response = await authorized_test_client.post("/users", json=payload)
    assert response.status_code == 200

    response = await authorized_test_client.put(
        url="/user", json={"user": {update_field: update_value}}
    )
    assert response.status_code == 400
