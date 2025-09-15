import asyncio
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from rates.api.rates_ws import router
from rates.config import rates_config
from rates.database.deps import get_session_factory, get_async_engine
from rates.database.queries import select_assets
from rates.services import PointsBroker, PointsFetcher


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async_engine_deps = _app.dependency_overrides.get(get_async_engine, get_async_engine)
    session_factory_deps = _app.dependency_overrides.get(get_session_factory, get_session_factory)
    async_engine = async_engine_deps()
    session_factory = session_factory_deps(async_engine)
    http_client = httpx.AsyncClient(
        base_url=rates_config.fetcher_base_url,
    )
    points_broker = PointsBroker()
    async with session_factory() as session:
        assets = await select_assets(session)

    fetcher = PointsFetcher(
        http_client=http_client,
        points_broker=points_broker,
        assets=assets,
        session_factory=session_factory,
    )

    fetcher_task = asyncio.create_task(fetcher.run())

    _app.state.points_broker = points_broker

    yield

    await http_client.aclose()
    if not fetcher_task.done():
        fetcher_task.cancel()
    fetcher.stop()
    points_broker.stop()


app = FastAPI(lifespan=lifespan)

app.include_router(router)
