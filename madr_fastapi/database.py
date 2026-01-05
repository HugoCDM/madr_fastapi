from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from madr_fastapi.settings import Settings

engine = create_async_engine(url=Settings().DATABASE_URL)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
