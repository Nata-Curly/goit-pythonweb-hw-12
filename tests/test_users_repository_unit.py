import pytest
from unittest.mock import AsyncMock, MagicMock

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate


@pytest.fixture()
def db_session_mock():
    return AsyncMock()


@pytest.fixture()
def repository(db_session_mock):
    return UserRepository(db_session_mock)


@pytest.mark.asyncio
async def test_get_user_by_id(repository, db_session_mock):
    expected_user = User(id=1, username="testuser")
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = AsyncMock(return_value=expected_user)
    db_session_mock.execute = AsyncMock(return_value=mock_result)

    result = await repository.get_user_by_id(1)

    assert result == expected_user
    db_session_mock.execute.assert_awaited()
    mock_result.scalar_one_or_none.assert_awaited()


@pytest.mark.asyncio
async def test_get_user_by_username(repository, db_session_mock):
    expected_user = User(id=1, username="testuser")
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = AsyncMock(return_value=expected_user)
    db_session_mock.execute = AsyncMock(return_value=mock_result)

    result = await repository.get_user_by_username("testuser")

    assert result == expected_user
    db_session_mock.execute.assert_awaited()
    mock_result.scalar_one_or_none.assert_awaited()


@pytest.mark.asyncio
async def test_get_user_by_email(repository, db_session_mock):
    expected_user = User(id=1, email="user@example.com")
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = AsyncMock(return_value=expected_user)
    db_session_mock.execute = AsyncMock(return_value=mock_result)

    result = await repository.get_user_by_email("user@example.com")

    assert result == expected_user
    db_session_mock.execute.assert_awaited()
    mock_result.scalar_one_or_none.assert_awaited()


@pytest.mark.asyncio
async def test_create_user(repository, db_session_mock):
    body = UserCreate(
        username="newuser", email="new@example.com", password="pass123", role="user"
    )

    db_session_mock.add = MagicMock()
    db_session_mock.commit = AsyncMock()
    db_session_mock.refresh = AsyncMock()

    result_user = await repository.create_user(body)

    db_session_mock.add.assert_called()
    db_session_mock.commit.assert_awaited()
    db_session_mock.refresh.assert_awaited()
    assert isinstance(result_user, User)
    assert hasattr(result_user, "hashed_password")
    assert result_user.hashed_password == "pass123"


@pytest.mark.asyncio
async def test_confirmed_email(repository, db_session_mock):
    user_mock = MagicMock()
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = AsyncMock(return_value=user_mock)
    db_session_mock.execute = AsyncMock(return_value=mock_result)
    db_session_mock.commit = AsyncMock()

    await repository.confirmed_email("user@example.com")

    db_session_mock.commit.assert_awaited()


@pytest.mark.asyncio
async def test_confirmed_email_user_not_found(repository, db_session_mock):
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = AsyncMock(return_value=None)
    db_session_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(AttributeError):
        await repository.confirmed_email("nonexistent@example.com")
