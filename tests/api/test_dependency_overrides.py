import datetime

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from conduit.application.dtos.tag import TagDTO
from conduit.core.providers import get_tag_service


class _TagServiceStub:
    async def get_all_tags(self, *_: object, **__: object) -> list[TagDTO]:
        return [
            TagDTO(id=1, tag="override", created_at=datetime.datetime(2024, 1, 1)),
            TagDTO(id=2, tag="stubbed", created_at=datetime.datetime(2024, 1, 2)),
        ]


@pytest.mark.anyio
async def test_dependency_override_tag_service(application: FastAPI) -> None:
    async def _override_tag_service() -> _TagServiceStub:
        return _TagServiceStub()

    application.dependency_overrides[get_tag_service] = _override_tag_service
    try:
        async with AsyncClient(
            app=application,
            base_url="http://testserver/api",
            headers={"Content-Type": "application/json"},
        ) as client:
            response = await client.get(url="/tags")
        assert response.status_code == 200
        assert response.json() == {"tags": ["override", "stubbed"]}
    finally:
        application.dependency_overrides.pop(get_tag_service, None)
