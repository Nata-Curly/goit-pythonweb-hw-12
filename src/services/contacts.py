from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from src.repository.contacts import ContactRepository
from src.schemas import ContactBase, User


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
        return await self.repository.create_contact(body, user)

    async def get_contacts(self, skip: int, limit: int, user: User):
        return await self.repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactBase, user: User):
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        return await self.repository.remove_contact(contact_id, user)

    async def get_birthdays(self, user: User):
        return await self.repository.get_birthdays(user)

    async def search_contacts(
        self,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
        user: User,
    ):
        return await self.repository.search_contacts(first_name, last_name, email, user)
