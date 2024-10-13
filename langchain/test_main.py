import unittest
from fastapi.testclient import TestClient
from app import app

class TestMain(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)

    def test_read_status(self):
        # GET 요청을 보내고 응답을 검증d
        response = self.client.get("/status")
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json(), {"message": "Hello, World"})

    def test_create_chat(self):
        # POST 요청을 보내고 응답을 검증
        data = {
            "user_id": "1",  # 필요한 파라미터
            "conversation_id": "1",
            "scenario": "meeting",
            "difficulty": "Normal",  
            "input":"can you ask me?",
            "first": True
        }
        response = self.client.post("/chat", json=data)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json(), {"name": "TestItem"})

    def test_create_quiz(self):
        # POST 요청을 보내고 응답을 검증
        data = {
            "user_id": "1",  # 필요한 파라미터
            "conversation_id": "2",
            "quiz_type": "vocabulary",
            "difficulty": "Normal",  
            "input":"can you ask me?",
            "first": True
        }
        response = self.client.post("/quiz", json=data)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json(), {"name": "TestItem"})

if __name__ == "__main__":
    unittest.main()
