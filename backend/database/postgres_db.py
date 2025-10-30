import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import DatabaseConfig

class PostgresBase(DeclarativeBase):
    pass

# Database setup
engine = create_async_engine(DatabaseConfig.POSTGRES_URL, echo=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_postgres_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_postgres_tables():
    async with engine.begin() as conn:
        await conn.run_sync(PostgresBase.metadata.create_all)
    print("✅ PostgreSQL tables initialized!")

async def test_postgres_connection():
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        print("✅ PostgreSQL connection successful!")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False