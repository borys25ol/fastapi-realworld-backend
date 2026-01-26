from conduit.application.dtos.article import (
    ArticleAuthorDTO,
    ArticleDTO,
    ArticlesFeedDTO,
)
from conduit.application.dtos.profile import ProfileDTO
from conduit.application.queries.article_feed import ArticleFeedRecordDTO
from conduit.domain.entities.article import Article


def entity_to_article_dto(
    article: Article,
    profile: ProfileDTO,
    tags: list[str],
    favorited: bool,
    favorites_count: int,
) -> ArticleDTO:
    return ArticleDTO(
        id=article.id,
        author_id=article.author_id,
        slug=article.slug,
        title=article.title,
        description=article.description,
        body=article.body,
        author=ArticleAuthorDTO(
            username=profile.username,
            bio=profile.bio,
            image=profile.image,
            following=profile.following,
        ),
        tags=tags,
        favorited=favorited,
        favorites_count=favorites_count,
        created_at=article.created_at,
        updated_at=article.updated_at or article.created_at,
    )


def feed_record_to_article_dto(record: ArticleFeedRecordDTO) -> ArticleDTO:
    return ArticleDTO(
        id=record.id,
        author_id=record.author_id,
        slug=record.slug,
        title=record.title,
        description=record.description,
        body=record.body,
        tags=record.tags,
        author=ArticleAuthorDTO(
            username=record.author_username,
            bio=record.author_bio or "",
            image=record.author_image_url,
            following=record.author_following,
        ),
        created_at=record.created_at,
        updated_at=record.updated_at,
        favorited=record.favorited,
        favorites_count=record.favorites_count,
    )


def feed_records_to_articles_dto(
    records: list[ArticleFeedRecordDTO], articles_count: int
) -> ArticlesFeedDTO:
    return ArticlesFeedDTO(
        articles=[feed_record_to_article_dto(record) for record in records],
        articles_count=articles_count,
    )
