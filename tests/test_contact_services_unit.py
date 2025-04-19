import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.contacts import get_birthdays
from src.services.contacts import ContactService
from src.repository.contacts import ContactRepository
from src.schemas import ContactBase
from src.database.models import UserRole, User


@pytest.fixture()
def user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        avatar="https://example.com/avatar.png",
        role=UserRole.USER,
    )


@pytest.fixture()
def repository_mock():
    mock = MagicMock()
    mock.create_contact = AsyncMock(return_value="created")
    mock.get_contacts = AsyncMock(return_value=["contact1", "contact2"])
    mock.get_contact_by_id = AsyncMock(return_value="contact1")
    mock.update_contact = AsyncMock(return_value="updated")
    mock.remove_contact = AsyncMock(return_value="removed")
    mock.get_birthdays = AsyncMock(return_value=["birthday1"])
    mock.search_contacts = AsyncMock(return_value=["found1", "found2"])
    return mock


@pytest.fixture()
def service(repository_mock):
    service = ContactService(db=None)
    service.repository = repository_mock
    return service


@pytest.mark.asyncio
async def test_create_contact(service, repository_mock, user):
    body = ContactBase(first_name="John", last_name="Doe", email="john@example.com", phone_number="1234567890")

    result = await service.create_contact(body, user)

    assert result == "created"
    repository_mock.create_contact.assert_awaited_with(body, user)


@pytest.mark.asyncio
async def test_get_contacts(service, repository_mock, user):
    result = await service.get_contacts(0, 10, user)

    assert result == ["contact1", "contact2"]
    repository_mock.get_contacts.assert_awaited_with(0, 10, user)


@pytest.mark.asyncio
async def test_get_contact(service, repository_mock, user):
    result = await service.get_contact(1, user)

    assert result == "contact1"
    repository_mock.get_contact_by_id.assert_awaited_with(1, user)


@pytest.mark.asyncio
async def test_update_contact(service, repository_mock, user):
    body = ContactBase(
        first_name="Updated", last_name="Name", email="updated@example.com", phone_number="1234567890"
    )

    result = await service.update_contact(1, body, user)

    assert result == "updated"
    repository_mock.update_contact.assert_awaited_with(1, body, user)


@pytest.mark.asyncio
async def test_remove_contact(service, repository_mock, user):
    result = await service.remove_contact(1, user)

    assert result == "removed"
    repository_mock.remove_contact.assert_awaited_with(1, user)


@pytest.mark.asyncio
async def test_get_birthdays(service, repository_mock, user):
    result = await service.get_birthdays(user)

    assert result == ["birthday1"]
    repository_mock.get_birthdays.assert_awaited_with(user)


@pytest.mark.asyncio
async def test_search_contacts(service, repository_mock, user):
    result = await service.search_contacts("John", None, None, user)

    assert result == ["found1", "found2"]
    repository_mock.search_contacts.assert_awaited_with("John", None, None, user)


@pytest.mark.asyncio
async def test_get_contacts_zero_limit(service, repository_mock, user):
    result = await service.get_contacts(0, 0, user)
    assert result == ["contact1", "contact2"]
    repository_mock.get_contacts.assert_awaited_with(0, 0, user)


@pytest.mark.asyncio
async def test_get_contact_not_found(service, repository_mock, user):
    repository_mock.get_contact_by_id.return_value = None
    result = await service.get_contact(999, user)
    assert result is None
    repository_mock.get_contact_by_id.assert_awaited_with(999, user)


@pytest.mark.asyncio
async def test_search_contacts_full(service, repository_mock, user):
    result = await service.search_contacts("John", "Doe", "john@example.com", user)
    assert result == ["found1", "found2"]
    repository_mock.search_contacts.assert_awaited_with(
        "John", "Doe", "john@example.com", user
    )

