from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """This class definition is for a UserRepository that manages user data in a database.
    Note that this class uses SQLAlchemy for database operations and assumes the existence of a User model and a UserCreate schema.
    """
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get a user by id.

        Args:
            user_id (int): The user id.

        Returns:
            User | None: The user with the given id, or None if not found.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get a user by username.

        Args:
            username (str): The username to search for.

        Returns:
            User | None: The user with the given username, or None if not found.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by email.

        Args:
            email (str): The email to search for.

        Returns:
            User | None: The user with the given email, or None if not found.
        """

        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user in the database.

        Args:
            body (UserCreate): The user details to be created.
            avatar (str, optional): The avatar URL. Defaults to None.

        Returns:
            User: The newly created user object.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Confirms the user's email address.

        Args:
            email (str): The email address to be confirmed.

        Returns:
            None
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Updates the user's avatar URL.

        Args:
            email (str): The email address of the user to be updated.
            url (str): The new avatar URL.

        Returns:
            User: The updated user object.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
