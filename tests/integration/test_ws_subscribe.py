from fastapi.testclient import TestClient


def test_websocket_subscribe(client: TestClient, mock_rates_server):
    with client.websocket_connect("/rates-ws") as ws:
        ws.send_json({"action": "subscribe", "message": {"assetId": 1}})
        resp = ws.receive_json()

        assert "points" in resp["message"]
        assert isinstance(resp["message"]["points"], list)

        resp = ws.receive_json()

        assert mock_rates_server["rates"].called
        assert resp["action"] == "point"
        assert resp["message"]["assetName"] == "EURUSD"
        assert resp["message"]["value"] == 162.5075
