from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from src.repository.contacts import ContactRepository
from src.schemas import ContactBase, User


class ContactService:
    """
    Service class for handling contact operations.
    It acts as an interface between the business logic and the data storage, encapsulating the complexity of database operations.
    Note that all methods are asynchronous, indicating that they are designed to work with asynchronous database operations.
    """
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
        """
        Create a new contact in the database.

        Args:
            body (ContactBase): The contact details to be created.
            user (User): The user performing the request.

        Returns:
            Contact: The newly created contact object.
        """

        return await self.repository.create_contact(body, user)

    async def get_contacts(self, skip: int, limit: int, user: User):
        """
        Get a list of contacts.

        Args:
            skip (int): Skip the specified number of items.
            limit (int): Limit the number of items returned.
            user (User): User performing the request.

        Returns:
            List[Contact]: List of contacts.
        """
        return await self.repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Get a contact by id.

        Args:
            contact_id (int): ID of the contact.
            user (User): User performing the request.

        Returns:
            Optional[Contact]: Contact with the given id, or None if not found.
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactBase, user: User):
        """
        Update a contact by id.

        Args:
            contact_id (int): ID of the contact to be updated.
            body (ContactBase): The contact details to be updated.
            user (User): User performing the request.

        Returns:
            Optional[Contact]: The updated contact, or None if it does not exist.
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Remove a contact by id.

        Args:
            contact_id (int): ID of the contact to be removed.
            user (User): User performing the request.

        Returns:
            Optional[Contact]: The removed contact, or None if it does not exist.
        """
        return await self.repository.remove_contact(contact_id, user)

    async def get_birthdays(self, user: User):
        """
        Get contacts with birthdays within the next week.

        Args:
            user (User): User performing the request.

        Returns:
            List[Contact]: List of contacts with birthdays within the next week.
        """

        return await self.repository.get_birthdays(user)

    async def search_contacts(
        self,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
        user: User,
    ):
        """
        Search for contacts by first name, last name, or email.

        Args:
            first_name (Optional[str]): Filter by first name.
            last_name (Optional[str]): Filter by last name.
            email (Optional[str]): Filter by email.
            user (User): User performing the request.

        Returns:
            List[Contact]: List of contacts matching the search criteria.
        """
        return await self.repository.search_contacts(first_name, last_name, email, user)
