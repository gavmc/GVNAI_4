from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.config import settings

Base = declarative_base()


engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
async_session  = sessionmaker(binf=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session