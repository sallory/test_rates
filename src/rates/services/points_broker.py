import asyncio
from collections import defaultdict
from typing import AsyncIterator

from fastapi import WebSocket

from .points_fetcher import Point


class PointsBroker:
    def __init__(self) -> None:
        self._subscribers: dict[int, set[WebSocket]] = defaultdict(set)
        self._queues: dict[WebSocket, asyncio.Queue] = {}
        self._assets: dict[WebSocket, int] = {}
        self._stop_event = asyncio.Event()

    def create_queue(self, ws: WebSocket):
        self._queues[ws] = asyncio.Queue()

    async def publish(self, point: Point) -> None:
        if point["assetId"] not in self._subscribers:
            return
        for ws in self._subscribers[point["assetId"]]:
            queue = self._queues[ws]
            await queue.put(point)

    def subscribe(self, asset_id: int, ws: WebSocket):
        prev_asset_id = self._assets.pop(ws, None)
        if prev_asset_id is not None:
            self._subscribers[prev_asset_id].remove(ws)

        self._subscribers[asset_id].add(ws)
        self._assets[ws] = asset_id

    def unsubscribe(self, ws: WebSocket):
        asset_id = self._assets.get(ws)
        self._queues.pop(ws, None)
        if ws in self._subscribers[asset_id]:
            self._subscribers[asset_id].remove(ws)

    async def listen(self, ws: WebSocket) -> AsyncIterator[Point]:
        while not self._stop_event.is_set():
            msg = await self._queues[ws].get()
            yield msg

    def stop(self):
        self._stop_event.set()