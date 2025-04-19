import asyncio
from datetime import date

import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy import select
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src.database.models import Base, User, UserRole, Contact
from src.database.db import get_db
from src.services.auth import create_access_token, Hash


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)


test_user_data = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
    "role": UserRole.USER,
}

admin_user_data = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin12345",
    "role": UserRole.ADMIN,
}


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        user = User(
            username=test_user_data["username"],
            email=test_user_data["email"],
            hashed_password=Hash().get_password_hash(test_user_data["password"]),
            confirmed=True,
            avatar="https://twitter.com/gravatar",
            role=test_user_data["role"],
        )
        session.add(user)

        admin = User(
            username=admin_user_data["username"],
            email=admin_user_data["email"],
            hashed_password=Hash().get_password_hash(admin_user_data["password"]),
            confirmed=True,
            avatar="https://twitter.com/admin_gravatar",
            role=admin_user_data["role"],
        )
        session.add(admin)

        await session.commit()


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def user_token() -> str:
    token = await create_access_token(data={"sub": test_user_data["username"]})
    return token


@pytest_asyncio.fixture
async def admin_token() -> str:
    token = await create_access_token(data={"sub": admin_user_data["username"]})
    return token


@pytest_asyncio.fixture
async def test_user(session: AsyncSession) -> User:
    result = await session.execute(
        select(User).filter_by(email=test_user_data["email"])
    )
    return result.scalar_one()


@pytest_asyncio.fixture
async def contact(session: AsyncSession, test_user: User) -> Contact:
    contact = Contact(
        first_name="Test",
        last_name="Contact",
        email="test.contact@example.com",
        phone="1234567890",
        birth_date=date(1990, 1, 1),
        user=test_user,
    )
    session.add(contact)
    await session.commit()
    await session.refresh(contact)
    return contact

