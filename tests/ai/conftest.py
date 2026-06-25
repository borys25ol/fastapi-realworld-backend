import pytest


@pytest.fixture(autouse=True)
def create_tables():
    """AI tests are pure unit tests — override the root DB fixture with a no-op."""
    yield
