import asyncio
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from rates.database.deps import get_session_factory, SessionFactory
from rates.database.queries import select_asset_by_id, select_assets, select_points_by_asset
from rates.services import PointsBroker

router = APIRouter()


async def listen_ws(ws: WebSocket, points_broker: PointsBroker, session_factory: SessionFactory):
    # TODO: добавить валидацию запроса, разбить на действия, вынести в модуль
    while True:
        request = await ws.receive_json()
        async with session_factory() as session:
            if request["action"] == "assets":
                assets = await select_assets(session)
                await ws.send_json({
                    "action": "assets",
                    "assets": [asset.to_dict() for asset in assets],
                })
            elif request["action"] == "subscribe":
                asset_id = request["message"]["assetId"]
                asset = await select_asset_by_id(session, asset_id)
                if asset is None:
                    # TODO: добавить ошибки валидации
                    continue
                points = await select_points_by_asset(session, asset)
                await ws.send_json({
                    "message": {
                        "points": [point.to_dict() for point in points],
                    },
                })
                points_broker.subscribe(request["message"]["assetId"], ws)


async def send_points(ws: WebSocket, points_broker: PointsBroker):
    async for point in points_broker.listen(ws):
        await ws.send_json({
            "message": point,
            "action": "point",
        })


@router.websocket("/rates-ws")
async def websocket_endpoint(ws: WebSocket, session_factory: SessionFactory = Depends(get_session_factory)):
    await ws.accept()
    points_broker: PointsBroker = ws.app.state.points_broker
    points_broker.create_queue(ws)
    try:
        await asyncio.gather(
            listen_ws(ws, points_broker, session_factory),
            send_points(ws, points_broker),
        )
    except WebSocketDisconnect:
        logging.info("/rates-ws: disconnected")
    finally:
        points_broker.unsubscribe(ws)
