import abc
from types import TracebackType

from conduit.domain.repositories.article import IArticleRepository
from conduit.domain.repositories.article_tag import IArticleTagRepository
from conduit.domain.repositories.comment import ICommentRepository
from conduit.domain.repositories.favorite import IFavoriteRepository
from conduit.domain.repositories.follower import IFollowerRepository
from conduit.domain.repositories.tag import ITagRepository
from conduit.domain.repositories.user import IUserRepository


class IUnitOfWork(abc.ABC):
    """Abstract unit of work contract for transactional operations."""

    users: IUserRepository
    articles: IArticleRepository
    article_tags: IArticleTagRepository
    comments: ICommentRepository
    favorites: IFavoriteRepository
    followers: IFollowerRepository
    tags: ITagRepository

    @abc.abstractmethod
    async def __aenter__(self) -> "IUnitOfWork": ...

    @abc.abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    @abc.abstractmethod
    async def commit(self) -> None: ...

    @abc.abstractmethod
    async def rollback(self) -> None: ...
