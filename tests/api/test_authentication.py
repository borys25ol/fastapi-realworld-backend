import pytest
from httpx import AsyncClient

from conduit.domain.dtos.jwt import AuthTokenDTO

pytestmark = pytest.mark.asyncio


async def test_failed_login_with_invalid_token_prefix(
    test_client: AsyncClient, token_dto: AuthTokenDTO
) -> None:
    response = await test_client.get(
        url="/api/user", headers={"Authorization": f"JWTToken {token_dto.token}"}
    )
    assert response.status_code == 403


async def test_failed_login_when_user_does_not_exist(
    test_client: AsyncClient, not_exists_token_dto: AuthTokenDTO
) -> None:
    response = await test_client.get(
        url="/api/user",
        headers={"Authorization": f"Token {not_exists_token_dto.token}"},
    )
    assert response.status_code == 400
