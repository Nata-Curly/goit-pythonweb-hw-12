from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService


class Hash:
    """
    Hash class for password hashing and verification.
    Note that the pwd_context attribute is a CryptContext instance configured to use the bcrypt scheme, which is a widely used and secure password hashing algorithm.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies that a given plain password matches a given hashed password.

        Args:
            plain_password (str): The plain password to check.
            hashed_password (str): The hashed password to check against.

        Returns:
            bool: True if the passwords match, else False.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hashes a given password.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Creates an access token for the given data.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[int], optional): The number of seconds until
            the token should expire. Defaults to None.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Retrieves the current user based on the provided JWT token.

    This function decodes the provided JWT token to extract the username and
    retrieves the corresponding user from the database. If the token is invalid
    or the user does not exist, an HTTP exception is raised.

    Args:
        token (str): The JWT token used for authentication, obtained from
                     the request's authorization header.
        db (Session): The database session to use for retrieving the user.

    Returns:
        User: The user object corresponding to the token's subject.

    Raises:
        HTTPException: If the token cannot be validated or if the user does
                       not exist.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


def create_email_token(data: dict):
    """
    Creates a JWT token containing the given data that is valid for 7 days.

    Args:
        data (dict): The data to encode in the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """
    Validates a JWT token and extracts the email address from it.

    Args:
        token (str): The JWT token to validate.

    Returns:
        str: The email address encoded in the token.

    Raises:
        HTTPException: If the token is invalid or corrupted.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Невірний токен для перевірки електронної пошти",
        )
