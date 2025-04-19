import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.users import UserService
from src.schemas import UserCreate
from src.database.models import User, UserRole


@pytest.fixture()
def db_session_mock():
    return AsyncMock()


@pytest.fixture()
def user_service(db_session_mock):
    return UserService(db_session_mock)


@pytest.mark.asyncio
@patch("src.services.users.Gravatar")
async def test_create_user_with_avatar(mock_gravatar, user_service):
    body = UserCreate(username="user", email="user@example.com", password="pass123", role="user")
    avatar_url = "https://example.com/avatar.jpg"

    mock_gravatar_instance = MagicMock()
    mock_gravatar.return_value = mock_gravatar_instance
    mock_gravatar_instance.get_image.return_value = avatar_url

    user_service.repository.create_user = AsyncMock(return_value=User(username="user"))

    result = await user_service.create_user(body)

    mock_gravatar.assert_called_once_with(body.email)
    mock_gravatar_instance.get_image.assert_called_once()
    user_service.repository.create_user.assert_awaited_once_with(body, avatar_url)
    assert isinstance(result, User)


@pytest.mark.asyncio
async def test_get_user_by_id(user_service):
    expected_user = User(id=1)
    user_service.repository.get_user_by_id = AsyncMock(return_value=expected_user)

    result = await user_service.get_user_by_id(1)

    user_service.repository.get_user_by_id.assert_awaited_once_with(1)
    assert result == expected_user


@pytest.mark.asyncio
async def test_get_user_by_username(user_service):
    expected_user = User(username="user")
    user_service.repository.get_user_by_username = AsyncMock(return_value=expected_user)

    result = await user_service.get_user_by_username("user")

    user_service.repository.get_user_by_username.assert_awaited_once_with("user")
    assert result == expected_user


@pytest.mark.asyncio
async def test_get_user_by_email(user_service):
    expected_user = User(email="user@example.com")
    user_service.repository.get_user_by_email = AsyncMock(return_value=expected_user)

    result = await user_service.get_user_by_email("user@example.com")

    user_service.repository.get_user_by_email.assert_awaited_once_with(
        "user@example.com"
    )
    assert result == expected_user


@pytest.mark.asyncio
async def test_confirmed_email(user_service):
    user_service.repository.confirmed_email = AsyncMock()

    await user_service.confirmed_email("user@example.com")

    user_service.repository.confirmed_email.assert_awaited_once_with("user@example.com")


@pytest.mark.asyncio
async def test_confirmed_email_user_not_found(user_service):
    user_service.repository.confirmed_email = AsyncMock(
        side_effect=AttributeError("User not found")
    )

    with pytest.raises(AttributeError, match="User not found"):
        await user_service.confirmed_email("nonexistent@example.com")

    user_service.repository.confirmed_email.assert_awaited_once_with(
        "nonexistent@example.com"
    )


@pytest.mark.asyncio
async def test_update_avatar_url(user_service):
    updated_user = User(
        email="user@example.com", avatar="https://example.com/avatar.jpg"
    )
    user_service.repository.update_avatar_url = AsyncMock(return_value=updated_user)

    result = await user_service.update_avatar_url(
        "user@example.com", "https://example.com/avatar.jpg"
    )

    user_service.repository.update_avatar_url.assert_awaited_once_with(
        "user@example.com", "https://example.com/avatar.jpg"
    )
    assert result == updated_user


@pytest.mark.asyncio
async def test_update_avatar_url_user_not_found(user_service):
    user_service.repository.update_avatar_url = AsyncMock(
        side_effect=AttributeError("User not found")
    )

    with pytest.raises(AttributeError, match="User not found"):
        await user_service.update_avatar_url(
            "notfound@example.com", "http://img.com/avatar.png"
        )

    user_service.repository.update_avatar_url.assert_awaited_once_with(
        "notfound@example.com", "http://img.com/avatar.png"
    )
