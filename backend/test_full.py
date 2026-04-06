from fastapi.testclient import TestClient
from main import app

def test():
    with TestClient(app) as client:
        print("Testing valid text...")
        response = client.post("/analyze-text", json={"text": "President Biden announced a new infrastructure bill today in Washington. It is massive and very real."})
        print("Status Code:", response.status_code)
        if response.status_code != 200:
            print("Error details:", response.text)
        else:
            print("Success!")

if __name__ == "__main__":
    test()
