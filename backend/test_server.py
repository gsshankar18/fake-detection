import asyncio
import requests
import time

def test_running_server():
    print("Testing against running server")
    try:
        response = requests.post("http://127.0.0.1:8000/analyze-text", json={"text": "President Biden announced a new infrastructure bill today in Washington. It is massive and very real."})
        print("Status:", response.status_code)
        print("Response:", response.text)
    except Exception as e:
        print("Error calling server:", e)

if __name__ == "__main__":
    test_running_server()
