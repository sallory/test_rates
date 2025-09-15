from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rates.dto import AssetDTO
from rates.database.models import Asset


async def select_assets(session: AsyncSession) -> list[AssetDTO]:
    stmt = select(Asset)
    result = await session.execute(stmt)
    assets = [
        AssetDTO(id=asset.id, symbol=asset.symbol)
        for asset in result.scalars().all()
    ]
    return assets


async def select_asset_by_id(session: AsyncSession, asset_id: int) -> AssetDTO:
    stmt = select(Asset).where(Asset.id == asset_id)
    result = await session.execute(stmt)

    if asset := result.scalar_one_or_none():
        return AssetDTO(id=asset.id, symbol=asset.symbol)
