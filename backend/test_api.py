import asyncio
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
def test_endpoints():
    print("Testing /analyze-text")
    response = client.post("/analyze-text", json={"text": "President Biden announced a new infrastructure bill today in Washington. It is massive and very real."})
    print("Status:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    test_endpoints()
