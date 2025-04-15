from typing import List, Optional

from sqlalchemy import select, and_, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import date, timedelta

from src.database.models import Contact
from src.schemas import ContactBase, User


class ContactRepository:
    """
    This class definition is for a ContactRepository that manages contacts in a database.
    Note that this class uses SQLAlchemy for database operations and assumes the existence of a Contact model and a User model.
    """
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Get a list of contacts.

        Args:
            skip (int): Skip the specified number of items.
            limit (int): Limit the number of items returned.
            user (User): User performing the request.

        Returns:
            List[Contact]: List of contacts.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Optional[Contact]:
        """
        Get a contact by id.

        Args:
            contact_id (int): ID of the contact.
            user (User): User performing the request.

        Returns:
            Optional[Contact]: Contact with the given id, or None if not found.
        """

        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        """
        Create a new contact in the database.

        Args:
            body (ContactBase): The contact details to be created.
            user (User): The user performing the request.

        Returns:
            Contact: The newly created contact object.
        """

        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user=User) -> Optional[Contact]:
        """
        Remove a contact by id.

        Args:
            contact_id (int): ID of the contact to be removed.
            user (User, optional): User performing the request. Defaults to User.

        Returns:
            Optional[Contact]: The removed contact, or None if it does not exist.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase, user=User
    ) -> Optional[Contact]:
        """
        Update a contact by id.

        Args:
            contact_id (int): ID of the contact to be updated.
            body (ContactBase): The contact details to be updated.
            user (User, optional): User performing the request. Defaults to User.

        Returns:
            Optional[Contact]: The updated contact, or None if it does not exist.
        """

        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def get_birthdays(self, user=User) -> List[Contact]:
        """
        Get contacts with birthdays within the next week.

        Args:
            user (User, optional): User performing the request. Defaults to User.

        Returns:
            List[Contact]: List of contacts with birthdays within the next week.
        """
        today = date.today()
        next_week = today + timedelta(days=7)

        stmt = (
            select(Contact)
            .filter_by(user=user)
            .where(
                and_(
                    Contact.birth_date.is_not(None),
                    or_(
                        and_(
                            extract("month", Contact.birth_date) == today.month,
                            extract("day", Contact.birth_date) >= today.day,
                        ),
                        and_(
                            extract("month", Contact.birth_date) == next_week.month,
                            extract("day", Contact.birth_date) <= next_week.day,
                        ),
                    ),
                )
            )
        )

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def search_contacts(
        self,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
        user=User,
    ) -> List[Contact]:
        """
        Search for contacts by first name, last name, or email.

        Args:
            first_name (Optional[str]): Filter by first name.
            last_name (Optional[str]): Filter by last name.
            email (Optional[str]): Filter by email.
            user (User, optional): User performing the request. Defaults to User.

        Returns:
            List[Contact]: List of contacts matching the search criteria.
        """

        stmt = select(Contact).filter_by(user=user)

        filters = []
        if first_name:
            filters.append(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            filters.append(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            filters.append(Contact.email.ilike(f"%{email}%"))

        if filters:
            stmt = stmt.where(or_(*filters))

        result = await self.db.execute(stmt)
        return result.scalars().all()
