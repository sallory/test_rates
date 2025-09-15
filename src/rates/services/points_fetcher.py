import asyncio
import json
import logging
import time
import typing
from datetime import datetime, timezone

import httpx

from rates.dto import AssetDTO
from rates.database.deps import SessionFactory
from rates.database.queries import insert_points


if typing.TYPE_CHECKING:
    from .points_broker import PointsBroker


class SourcePoint(typing.TypedDict):
    Symbol: str
    Bid: float
    Ask: float


class Point(typing.TypedDict):
    assetId: int
    assetName: str
    time: int
    value: float


class PointsFetcher:
    def __init__(self, http_client: httpx.AsyncClient, points_broker: "PointsBroker", assets: list[AssetDTO],
                 session_factory: SessionFactory):
        self.http_client = http_client
        self.assets = assets
        self.symbol_to_id = {asset.symbol: asset.id for asset in assets}
        self.points_broker = points_broker
        self.session_factory = session_factory
        self._stop_event = asyncio.Event()

    async def run(self):
        while not self._stop_event.is_set():
            start_time = time.time()
            try:
                ts, points = await self._fetch_points()
            except Exception as exc:
                logging.warning("Exception while fetching points: ", exc_info=exc)
                await asyncio.sleep(1 - (time.time() - start_time))
                continue

            parsed_points = self.parse_points(ts, points)

            for point in parsed_points:
                await self.points_broker.publish(point)
            await self._save_points(parsed_points, ts)
            await asyncio.sleep(1 - (time.time() - start_time))

    def parse_points(self, ts: int, points: list[SourcePoint]) -> list[Point]:
        result = []
        for point in points:
            if point["Symbol"] in self.symbol_to_id:
                result.append({
                    "assetId": self.symbol_to_id[point["Symbol"]],
                    "assetName": point["Symbol"],
                    "time": ts,
                    "value": (point["Bid"] + point["Ask"]) / 2
                })
        return result

    async def _fetch_points(self) -> tuple[int, list[SourcePoint]]:
        start_time = time.time()

        resp = await self.http_client.get(url="/")
        resp.raise_for_status()

        end_time = time.time()

        resp_text = resp.text[len("null("):-3]
        resp_json = json.loads(resp_text)

        rates = typing.cast(list[SourcePoint], resp_json["Rates"])
        ts = int((start_time + end_time) / 2)
        return ts, rates

    async def _save_points(self, points: list[Point], ts: float):
        db_points = []
        for point in points:
            db_point = {
                "asset_id": point["assetId"],
                "value": point["value"],
                "timestamp": datetime.fromtimestamp(ts, tz=timezone.utc),
            }
            db_points.append(db_point)

        async with self.session_factory() as session:
            await insert_points(session, db_points)

    def stop(self):
        self._stop_event.set()
