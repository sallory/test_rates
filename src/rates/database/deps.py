import typing

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession

from .builder import build_sa_engine, build_sa_session_factory


SessionFactory: typing.TypeAlias = async_sessionmaker[AsyncSession]


def get_async_engine() -> AsyncEngine:
    return build_sa_engine()


def get_session_factory(
    async_engine: AsyncEngine = Depends(get_async_engine),
) -> SessionFactory:
    return build_sa_session_factory(async_engine)
