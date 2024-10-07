from fastapi.testclient import TestClient
from ..app import app 

client = TestClient(app)

def test_healthz():
    # /healthz 엔드포인트에 GET 요청을 보냅니다.
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
