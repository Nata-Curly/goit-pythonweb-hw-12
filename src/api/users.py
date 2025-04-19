from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File

from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import UserRole
from src.schemas import User
from src.conf.config import settings
from src.services.auth import get_admin_user, get_current_user
from src.services.users import UserService
from src.services.upload_file import UploadFileService


router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=User, description="No more than 7 requests per minute"
)
@limiter.limit("7/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Get current user.

    Requires authorization header with JWT token.

    Returns:
        User: Current user.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user avatar.

    Requires authorization header with JWT token.

    Returns:
        User: Updated user.
    """

    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)


    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
