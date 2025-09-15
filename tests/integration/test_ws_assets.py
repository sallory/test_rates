from fastapi.testclient import TestClient

ASSETS = [
    {"id": 1, "symbol": "EURUSD"},
    {"id": 2, "symbol": "USDJPY"},
    {"id": 3, "symbol": "GBPUSD"},
    {"id": 4, "symbol": "AUDUSD"},
    {"id": 5, "symbol": "USDCAD"},
]


def test_websocket_assets(client: TestClient):
    with client.websocket_connect("/rates-ws") as ws:
        ws.send_json({"action": "assets"})
        resp = ws.receive_json()

        assert resp["action"] == "assets"
        assert resp["assets"] == ASSETS
