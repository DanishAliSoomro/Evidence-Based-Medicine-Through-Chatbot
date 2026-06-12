from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings

# engine = create_async_engine(settings.DATABASE_URL, echo=True)
engine = create_async_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()

# Use the more modern async_sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
