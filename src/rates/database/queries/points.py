from datetime import datetime, timedelta, timezone

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from rates.dto import AssetDTO, PointDTO
from rates.database.models import Point


async def insert_points(session: AsyncSession, points: list[dict]) -> None:
    stmt = insert(Point).values(points)
    await session.execute(stmt)
    await session.commit()


async def select_points_by_asset(session: AsyncSession, asset: AssetDTO) -> list[PointDTO]:
    # TODO: вынести константу в конфиг
    timestamp_from = datetime.now(tz=timezone.utc) - timedelta(minutes=30)
    stmt = (
        select(Point)
        .where(Point.asset_id == asset.id)
        .where(Point.timestamp >= timestamp_from)
        .order_by(Point.timestamp.asc())
    )
    result = await session.execute(stmt)
    points = [
        PointDTO(assetName=asset.symbol, time=int(point.timestamp.timestamp()), assetId=asset.id, value=point.value)
        for point in result.scalars().all()
    ]
    return points
