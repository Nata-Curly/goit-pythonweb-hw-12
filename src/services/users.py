from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    """
    The UserService class is a service layer that encapsulates user-related operations, providing a interface to interact with the user repository.
    """
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a new user in the database.

        Args:
            body (UserCreate): The user details to be created.

        Returns:
            User: The newly created user object.
        """

        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Get a user by id.

        Args:
            user_id (int): The user id.

        Returns:
            User | None: The user with the given id, or None if not found.
        """

        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Get a user by username.

        Args:
            username (str): The username to search for.

        Returns:
            User | None: The user with the given username, or None if not found.
        """

        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Get a user by email.

        Args:
            email (str): The email to search for.

        Returns:
            User | None: The user with the given email, or None if not found.
        """

        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Confirms the user's email address.

        Args:
            email (str): The email address to be confirmed.

        Returns:
            None
        """

        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Updates the user's avatar URL.

        Args:
            email (str): The email address of the user to be updated.
            url (str): The new avatar URL.

        Returns:
            User: The updated user object.
        """
        return await self.repository.update_avatar_url(email, url)
