from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import pool
from config import postgres_url

engine = create_async_engine(url=postgres_url, echo=False, future=True, poolclass=pool.QueuePool)
session_engine = async_sessionmaker(engine, expire_on_commit=False,  class_=AsyncSession)

async def get_db_session():
    async with session_engine() as session:
        yield session