import unittest
from fastapi.testclient import TestClient
from app import app

class TestMain(unittest.TestCase):
    
    def setUp(self):
        # TestClient를 사용해 FastAPI 앱을 테스트할 수 있도록 설정합니다.
        self.client = TestClient(app)

    def test_read_status(self):
        # GET 요청을 보내고 응답을 검증합니다.
        response = self.client.get("/status")
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json(), {"message": "Hello, World"})

    def test_create_chat(self):
        # POST 요청을 보내고 응답을 검증합니다.
        response = self.client.post("/chat")
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json(), {"name": "TestItem"})

    def test_create_quiz(self):
        # POST 요청을 보내고 응답을 검증합니다.
        response = self.client.post("/quiz")
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json(), {"name": "TestItem"})

    # def test_create_item_without_name(self):
    #     # 쿼리 파라미터 없이 POST 요청을 보내고 응답을 검증합니다.
    #     response = self.client.post("/test")
    #     self.assertEqual(response.status_code, 422)  # FastAPI는 유효하지 않은 요청에 대해 422를 반환합니다.

if __name__ == "__main__":
    unittest.main()
