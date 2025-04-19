import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from src.database.models import User, UserRole
from src.services.auth import create_access_token, Hash
from src.conf.config import settings

pytestmark = pytest.mark.asyncio

register_data = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword",
}


async def test_register_user(client: AsyncClient):
    response = await client.post("/auth/register", json=register_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == register_data["username"]
    assert data["email"] == register_data["email"]
    assert "id" in data


async def test_register_user_conflict_email(client: AsyncClient):
    response = await client.post("/auth/register", json=register_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "Користувач з таким email вже існує"


async def test_login_user(client: AsyncClient, session: AsyncSession):
    user = await session.execute(
        User.__table__.select().where(User.email == register_data["email"])
    )
    user_obj = user.scalar_one()
    user_obj.confirmed = True
    session.add(user_obj)
    await session.commit()

    login_data = {
        "username": register_data["email"],
        "password": register_data["password"],
    }

    response = await client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    login_data = {"username": register_data["email"], "password": "wrongpassword"}
    response = await client.post("/auth/login", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Неправильний логін або пароль"


async def test_request_email(client: AsyncClient):
    response = await client.post(
        "/auth/request_email", json={"email": register_data["email"]}
    )
    assert response.status_code == 200
    assert "message" in response.json()


async def test_confirmed_email(client: AsyncClient):
    token = await create_access_token(data={"sub": register_data["email"]})
    response = await client.get(f"/auth/confirmed_email/{token}")
    assert response.status_code == 200
    assert response.json()["message"] in [
        "Електронну пошту підтверджено",
        "Ваша електронна пошта вже підтверджена",
    ]


async def test_forgot_password(client: AsyncClient):
    response = await client.post(
        "/auth/forgot-password", json={"email": register_data["email"]}
    )
    assert response.status_code == 200
    assert (
        response.json()["message"]
        == "If that email exists, a reset link has been sent."
    )


async def test_reset_password(client: AsyncClient):
    token = jwt.encode(
        {"sub": register_data["email"]},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    response = await client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": "newsecurepassword"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password successfully reset."

