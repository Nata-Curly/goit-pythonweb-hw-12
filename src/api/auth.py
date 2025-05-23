from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status
from jose import jwt, JWTError

from src.schemas import UserCreate, Token, User, RequestEmail, ResetPassword
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
    get_admin_user,
)
from src.services.users import UserService
from src.services.email import send_email
from src.services.email import send_reset_password_email
from src.database.db import get_db
from src.conf.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Registers a new user in the system.

    Checks if a user with the provided email or username already exists. If not,
    hashes the password and creates a new user record in the database. Sends a
    confirmation email to the new user.

    Args:
        user_data (UserCreate): The user data including username, email, and password.
        background_tasks (BackgroundTasks): FastAPI BackgroundTasks instance for email sending.
        request (Request): The current request instance.
        db (Session): Database session dependency.

    Returns:
        User: The newly created user object.

    Raises:
        HTTPException: If a user with the same email or username already exists.
    """

    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticates a user and returns an access token.

    This function checks the provided username and password against
    the stored credentials. If the credentials are valid and the user's
    email is confirmed, it generates and returns a JWT access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing
            the username and password.
        db (Session): Database session dependency.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: If the username or password is incorrect, or if
        the user's email is not confirmed.
    """

    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )
    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirms the user's email address using the provided token.

    This function checks whether the provided token is valid and confirms
    the user's email address if it is. If the email is already confirmed, it
    returns a success message.

    Args:
        token (str): The verification token provided by email.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Requests an email with a verification link to be sent to the provided email address.

    This function checks whether the provided email address is already confirmed
    and if so, returns a success message. If the email address is not confirmed,
    it sends an email with a verification link to the email address.

    Args:
        body (RequestEmail): The email address to be verified.
        background_tasks (BackgroundTasks): FastAPI BackgroundTasks instance for email sending.
        request (Request): The current request instance.
        db (Session): Database session dependency.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If the email address is invalid or the user does not exist.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.post("/forgot-password")
async def forgot_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Requests an email with a reset password link to be sent to the provided email address.

    This function checks whether the provided email address is associated with a user
    and if so, sends an email with a reset password link to the email address.

    Args:
        body (RequestEmail): The email address to be verified.
        background_tasks (BackgroundTasks): FastAPI BackgroundTasks instance for email sending.
        db (Session): Database session dependency.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If the email address is invalid or the user does not exist.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user:
        from src.services.auth import create_reset_token

        token = create_reset_token({"sub": user.email})
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        background_tasks.add_task(send_reset_password_email, user.email, reset_link)
    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(body: ResetPassword, db: Session = Depends(get_db)):
    """
    Resets the user's password using the provided token and new password.

    Args:
        body (ResetPassword): The token and new password to reset the user's password.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            body.token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise credentials_exception

    user.hashed_password = Hash().get_password_hash(body.new_password)
    await db.commit()
    return {"message": "Password successfully reset."}


@router.get("/admin")
def read_admin(current_user: User = Depends(get_admin_user)):
    """
    Retrieves the current admin user and returns a welcome message.

    This endpoint is accessible only to users with admin privileges. The function uses
    a dependency to verify and retrieve the current admin user.

    Args:
        current_user (User): The current admin user, as returned by get_admin_user.

    Returns:
        dict: A dictionary containing a welcome message for the admin user.
    """

    return {"message": f"Hello {current_user.username}! Welcome to Admin Panel."}
