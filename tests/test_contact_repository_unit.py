import pytest
from unittest.mock import AsyncMock

from src.repository.contacts import ContactRepository
from src.schemas import ContactBase
from src.database.models import Contact, UserRole, User


@pytest.fixture()
def test_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        avatar="https://example.com/avatar.png",
        role=UserRole.USER,
    )


@pytest.fixture()
def session_mock():
    return AsyncMock()


@pytest.fixture()
def repo(session_mock):
    return ContactRepository(session_mock)


@pytest.mark.asyncio
async def test_get_contacts(repo, session_mock, test_user):
    mock_result = AsyncMock()
    mock_scalars = AsyncMock()
    mock_scalars.scalars.return_value = AsyncMock(
        ["contact1", "contact2"]
    )
    mock_result.scalars.return_value = mock_scalars
    session_mock.execute.return_value = mock_result

    result = await repo.get_contacts(0, 10, test_user)

    assert result == ["contact1", "contact2"]
    session_mock.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_contact_by_id(repo, session_mock, test_user):
    mock_result = AsyncMock()
    mock_result.scalars.one_or_none.return_value = AsyncMock("contact1")
    session_mock.execute.return_value = mock_result

    result = await repo.get_contact_by_id(1, test_user)

    assert result == "contact1"
    session_mock.execute.assert_awaited()


@pytest.mark.asyncio
async def test_create_contact(repo, session_mock, test_user):
    body = ContactBase(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone_number="1234567890",
    )
    session_mock.refresh = AsyncMock()

    result = await repo.create_contact(body, test_user)

    session_mock.add.assert_called()
    session_mock.commit.assert_awaited()
    session_mock.refresh.assert_awaited()
    assert isinstance(result, Contact)


@pytest.mark.asyncio
async def test_remove_contact_found(repo, session_mock, test_user):
    repo.get_contact_by_id = AsyncMock(return_value="contact1")

    result = await repo.remove_contact(1, test_user)

    assert result == "contact1"
    session_mock.delete.assert_awaited()
    session_mock.commit.assert_awaited()


@pytest.mark.asyncio
async def test_remove_contact_not_found(repo, test_user):
    repo.get_contact_by_id = AsyncMock(return_value=None)

    result = await repo.remove_contact(1, test_user)

    assert result is None


@pytest.mark.asyncio
async def test_update_contact(repo, session_mock, test_user):
    contact = Contact(
        id=1,
        first_name="Old",
        last_name="Name",
        email="old@example.com",
        phone_number="1234567890",
        user=test_user,
    )
    repo.get_contact_by_id = AsyncMock(return_value=contact)

    body = ContactBase(
        first_name="New",
        last_name="Name",
        email="new@example.com",
        phone_number="1234567890",
    )

    result = await repo.update_contact(1, body, test_user)

    assert result.first_name == "New"
    assert result.email == "new@example.com"
    session_mock.commit.assert_awaited()
    session_mock.refresh.assert_awaited()


@pytest.mark.asyncio
async def test_get_birthdays(repo, session_mock, test_user):
    mock_result = AsyncMock()
    mock_scalars = AsyncMock()
    mock_scalars.scalars.return_value = AsyncMock(["contact1"])
    mock_result.scalars.return_value = mock_scalars
    session_mock.execute.return_value = mock_result

    result = await repo.get_birthdays(test_user)

    assert result == ["contact1"]
    session_mock.execute.assert_awaited()


@pytest.mark.asyncio
async def test_search_contacts(repo, session_mock, test_user):
    mock_result = AsyncMock()
    mock_scalars = AsyncMock()
    mock_scalars.scalars.return_value = AsyncMock(
        ["result1", "result2"]
    )
    mock_result.scalars.return_value = mock_scalars
    session_mock.execute.return_value = mock_result

    result = await repo.search_contacts("John", None, None, test_user)

    assert result == ["result1", "result2"]
    session_mock.execute.assert_awaited()


@pytest.mark.asyncio
async def test_update_contact_not_found(repo, test_user):
    repo.get_contact_by_id = AsyncMock(return_value=None)
    body = ContactBase(
        first_name="New",
        last_name="Name",
        email="new@example.com",
        phone_number="1234567890",
    )

    result = await repo.update_contact(1, body, test_user)

    assert result is None
