import pytest
from httpx import AsyncClient

from conduit.domain.dtos.article import ArticleDTO


@pytest.mark.anyio
async def test_empty_list_when_no_tags_exist(test_client: AsyncClient) -> None:
    response = await test_client.get(url="/tags")
    assert response.json() == {"tags": []}


@pytest.mark.anyio
async def test_list_of_tags_when_article_with_tags_exists(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.get(url="/tags")
    response_tags = response.json()["tags"]
    assert len(response_tags) == len(set(test_article.tags))
    assert all(tag in test_article.tags for tag in response_tags)
