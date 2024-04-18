import pytest
from httpx import AsyncClient

from conduit.domain.dtos.user import UserDTO


@pytest.mark.anyio
async def test_user_successful_login(
    test_client: AsyncClient, test_user: UserDTO
) -> None:
    payload = {"user": {"email": "test@gmail.com", "password": "password"}}
    response = await test_client.post("/users/login", json=payload)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "credentials,",
    (
        {"email": "invalid@gmail.com", "password": "password"},
        {"email": "test@gmail.com", "password": "invalid"},
    ),
)
@pytest.mark.anyio
async def test_user_login_with_invalid_credentials_part(
    test_client: AsyncClient, credentials: dict
) -> None:
    payload = {"user": credentials}
    response = await test_client.post("/users/login", json=payload)
    assert response.status_code == 400
