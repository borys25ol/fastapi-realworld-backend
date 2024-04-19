import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_successful_health_check(test_client: AsyncClient) -> None:
    response = await test_client.get("/health-check")
    assert response.status_code == 200

    response = response.json()
    assert response["message"] == "Conduit Realworld API"
