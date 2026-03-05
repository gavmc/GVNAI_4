from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config import settings
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.sandbox import session_manager

Base = declarative_base()

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
async_session  = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await session_manager.close_all()
