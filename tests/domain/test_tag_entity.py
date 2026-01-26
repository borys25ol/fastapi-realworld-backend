import datetime

import pytest

from conduit.domain.entities.tag import Tag


@pytest.mark.parametrize("invalid_tag", ["", "  "])
def test_tag_rename_validates(invalid_tag: str) -> None:
    tag = Tag(id=1, tag="tag", created_at=datetime.datetime.now())
    with pytest.raises(ValueError):
        tag.rename(invalid_tag)
