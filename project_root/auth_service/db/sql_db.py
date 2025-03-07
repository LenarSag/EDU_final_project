from collections.abc import AsyncIterator

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from project_root.config.config import settings
from project_root.infrastructure import models

engine = create_async_engine(url=settings.db_test, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


# Function to check existing tables and create if necessary
def check_existing_tables_and_create(sync_conn) -> None:
    inspector = inspect(sync_conn)
    existing_tables = inspector.get_table_names()

    if not existing_tables:
        models.Base.metadata.create_all(sync_conn)


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(check_existing_tables_and_create)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
