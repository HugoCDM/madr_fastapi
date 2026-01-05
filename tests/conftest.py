import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from madr_fastapi.app import app
from madr_fastapi.database import get_session
from madr_fastapi.models import Book, Novelist, User, table_registry
from madr_fastapi.security import get_password_hash
from madr_fastapi.settings import Settings


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Faker('name')
    email = factory.Faker('email')
    password = factory.Faker('password')


class NovelistFactory(factory.Factory):
    class Meta:
        model = Novelist

    name = factory.Sequence(lambda n: f'Nome {n}'.strip().lower())


class BookFactory(factory.Factory):
    class Meta:
        model = Book

    year = factory.Sequence(lambda n: 1990 + int(n))
    title = factory.LazyAttribute(lambda n: f'Nome {n.year}'.strip().lower())
    novelist_id = factory.LazyAttribute(lambda n: n.year - 1989)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:18', driver='psycopg') as postgres:
        yield create_async_engine(postgres.get_connection_url())


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    password = 'secret'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def other_user(session: AsyncSession):
    password = 'secret'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


@pytest_asyncio.fixture
async def novelist(session: AsyncSession):
    novelist = NovelistFactory()
    session.add(novelist)
    await session.commit()
    await session.refresh(novelist)
    return novelist


@pytest_asyncio.fixture
async def book(session: AsyncSession, novelist):
    book = BookFactory(novelist_id=novelist.id)
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


@pytest_asyncio.fixture
async def settings():
    return Settings()
