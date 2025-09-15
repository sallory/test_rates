import pytest
import respx

from httpx import Response
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from rates.config import db_config, rates_config
from rates.database.deps import get_session_factory
from rates.main import app

RATES_MOCK_RESPONSE = 'null({"Rates":[{"Symbol":"EURUSD","Bid":162.491,"Ask":162.524,"Spread":3.30}]});\n'


def get_test_async_engine():
    return create_async_engine(
        db_config.database_url,
        echo=False,
    )


def get_test_session_factory(async_engine=Depends(get_test_async_engine)):
    session_factory = async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False)
    return session_factory


@pytest.fixture
def mock_rates_server():
    with respx.mock(
        base_url=rates_config.fetcher_base_url, assert_all_called=False
    ) as respx_mock:
        route = respx_mock.get("/", name="rates")
        route.return_value = Response(200, text=RATES_MOCK_RESPONSE)
        yield respx_mock


@pytest.fixture(autouse=True, scope="session")
def client():
    app.dependency_overrides[get_test_async_engine] = get_test_async_engine
    app.dependency_overrides[get_session_factory] = get_test_session_factory

    with TestClient(app) as client:
        yield client
