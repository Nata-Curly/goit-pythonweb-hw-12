from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db

from src.schemas import ContactBase, ContactResponse, User
from src.services.contacts import ContactService
from src.services.auth import get_current_user


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get a list of contacts.

    Args:
        skip (int): Skip the specified number of items. Defaults to 0.
        limit (int): Limit the number of items returned. Defaults to 10.
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).
        user (User, optional): User performing the request. Defaults to Depends(get_current_user).

    Returns:
        List[ContactResponse]: List of contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get contacts with birthdays within the next week.

    Args:
        db (AsyncSession): Database session.
        user (User): User performing the request.

    Returns:
        List[ContactResponse]: List of contacts with birthdays within the next week.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_birthdays(user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get a contact by id.

    Args:
        contact_id (int): ID of the contact.
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).
        user (User, optional): User performing the request. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 404 if the contact is not found.

    Returns:
        ContactResponse: Contact with the given id.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactBase,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new contact.

    Args:
        body (ContactBase): Contact details.
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).
        user (User, optional): User performing the request. Defaults to Depends(get_current_user).

    Returns:
        ContactResponse: Created contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.create_contact(body, user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactBase,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update a contact by id.

    Args:
        body (ContactBase): Contact details to be updated.
        contact_id (int): ID of the contact to be updated.
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).
        user (User, optional): User performing the request. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 404 if the contact is not found.

    Returns:
        ContactResponse: Updated contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete a contact by id.

    Args:
        contact_id (int): ID of the contact to be deleted.
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).
        user (User, optional): User performing the request. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 404 if the contact is not found.

    Returns:
        ContactResponse: Deleted contact.
    """

    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get("/contacts/search", response_model=List[ContactResponse])
async def search_contacts(
    first_name: Optional[str] = Query(None, min_length=1),
    last_name: Optional[str] = Query(None, min_length=1),
    email: Optional[str] = Query(None, min_length=3),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Search for contacts by first name, last name, or email.

    This endpoint allows users to search for contacts using optional query parameters
    such as first name, last name, and email. If a contact matches any of the provided
    parameters, it will be included in the response.

    Args:
        first_name (Optional[str]): Filter by first name. Minimum length of 1 character.
        last_name (Optional[str]): Filter by last name. Minimum length of 1 character.
        email (Optional[str]): Filter by email. Minimum length of 3 characters.
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).
        user (User, optional): User performing the request. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 404 if no contacts are found matching the search criteria.

    Returns:
        List[ContactResponse]: List of contacts matching the search criteria.
    """

    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(first_name, last_name, email, user)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contacts
