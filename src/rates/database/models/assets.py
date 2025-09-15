from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Asset(Base):
    __tablename__ = 'assets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    points: Mapped[list['Point']] = relationship(
        back_populates='asset',
        cascade='all, delete-orphan',
    )
