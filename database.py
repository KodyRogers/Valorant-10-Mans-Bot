from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file
DATABASE_URL = "sqlite+aiosqlite:///./bot.db"

# Async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True if you want SQL logs
    future=True
)

# Async session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


# Initialize database tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Dependency/helper for sessions
async def get_session():
    async with SessionLocal() as session:
        yield session