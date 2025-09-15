from __future__ import annotations

from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Point(Base):
    __tablename__ = 'points'

    asset_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('assets.id', ondelete='CASCADE'),
        primary_key=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        primary_key=True,
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)

    asset: Mapped['Asset'] = relationship(back_populates='points')
