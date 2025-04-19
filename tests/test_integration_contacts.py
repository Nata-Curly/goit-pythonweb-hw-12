import pytest
from datetime import date, timedelta
from httpx import AsyncClient


from src.database.models import Contact
from src.schemas import ContactBase, User
from src.repository.contacts import ContactRepository

@pytest.mark.asyncio
async def test_update_contact(client: AsyncClient, test_user: User):
    repo = ContactRepository(client)
    contact = await repo.create_contact(
        ContactBase(first_name="Old", last_name="Name", email="old@example.com"),
        test_user,
    )

    updated = await repo.update_contact(
        contact.id,
        ContactBase(first_name="New", last_name="Name", email="new@example.com"),
        test_user,
    )

    assert updated.first_name == "New"
    assert updated.email == "new@example.com"


@pytest.mark.asyncio
async def test_remove_contact(client: AsyncClient, test_user: User):
    repo = ContactRepository(client)
    contact = await repo.create_contact(
        ContactBase(first_name="ToDelete", last_name="Test", email="del@example.com", phone_number="1234567890"),
        test_user,
    )

    deleted = await repo.remove_contact(contact.id, test_user)
    assert deleted.id == contact.id

    should_be_none = await repo.get_contact_by_id(contact.id, test_user)
    assert should_be_none is None


@pytest.mark.asyncio
async def test_get_contacts(client: AsyncClient, test_user: User):
    repo = ContactRepository(client)

    await repo.create_contact(
        ContactBase(first_name="A", last_name="A", email="a@example.com", phone_number="1234567890"), test_user
    )
    await repo.create_contact(
        ContactBase(first_name="B", last_name="B", email="b@example.com", phone_number="1234567890"), test_user
    )

    result = await repo.get_contacts(skip=0, limit=10, user=test_user)
    assert len(result) >= 2


@pytest.mark.asyncio
async def test_get_birthdays(client: AsyncClient, test_user: User):
    repo = ContactRepository(client)

    today = date.today()
    upcoming_birthday = ContactBase(
        first_name="BD",
        last_name="Soon",
        email="bd@example.com",
        birth_date=today + timedelta(days=3),
        phone_number="1234567890",
    )

    await repo.create_contact(upcoming_birthday, test_user)

    results = await repo.get_birthdays(user=test_user)
    assert any(c.email == "bd@example.com" for c in results)


@pytest.mark.asyncio
async def test_search_contacts(client: AsyncClient, test_user: User):
    repo = ContactRepository(client)

    await repo.create_contact(
        ContactBase(
            first_name="UniqueName", last_name="Search", email="search@example.com", phone_number="1234567890"
        ),
        test_user,
    )

    results = await repo.search_contacts(
        first_name="unique", last_name=None, email=None, user=test_user
    )
    assert any("search@example.com" == c.email for c in results)
