from datetime import datetime
from fastapi import HTTPException
import pytest
from jose import jwt
from unittest.mock import AsyncMock, patch

from src.database.models import User, UserRole
from src.services import auth
from src.conf.config import settings


@pytest.mark.asyncio
async def test_get_password_hash_and_verify():
    password = "test_password123"
    hash_service = auth.Hash()
    hashed = hash_service.get_password_hash(password)

    assert isinstance(hashed, str)
    assert hashed != password
    assert hash_service.verify_password(password, hashed)



@pytest.mark.asyncio
async def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = await auth.create_access_token(data, expires_delta=1800)  # 30 minutes

    assert isinstance(token, str)
    decoded = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    assert decoded["sub"] == data["sub"]
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_create_email_token():
    data = {"sub": "user@example.com"}
    token = auth.create_email_token(data)

    assert isinstance(token, str)
    decoded = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    assert decoded["sub"] == data["sub"]
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_get_email_from_token_valid():
    data = {"sub": "user@example.com"}
    token = auth.create_email_token(data)
    result = await auth.get_email_from_token(token)

    assert result == data["sub"]


@pytest.mark.asyncio
async def test_get_admin_user_success():
    user = User(
        id=1,
        username="admin",
        email="admin@example.com",
        role=UserRole.ADMIN,
        avatar="",
        confirmed=True,          
        hashed_password="hashedpassword",
        created_at=datetime.now()
    )
    result = await auth.get_admin_user(current_user=user)
    assert result == user


@pytest.mark.asyncio
async def test_get_admin_user_forbidden():
    user = User(
        id=1,
        username="user",
        email="user@example.com",
        role=UserRole.USER,
        avatar="",
        confirmed=True,
        hashed_password="hashedpassword",
        created_at=datetime.now(),
    )

    with pytest.raises(HTTPException) as exc_info:
        await auth.get_admin_user(current_user=user)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_get_current_user_from_redis(monkeypatch):
    fake_token = auth.create_reset_token({"sub": "admin@example.com"})
    fake_user = {
        "id": "1",
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "avatar": "",
        "confirmed": "true",
    }

    mock_redis = AsyncMock()
    mock_redis.hgetall.return_value = fake_user

    monkeypatch.setattr(auth, "redis_client", mock_redis)

    with patch(
        "src.services.auth.jwt.decode", return_value={"sub": "admin@example.com"}
    ):
        user = await auth.get_current_user(fake_token, db=AsyncMock())
        assert user.username == "admin"
