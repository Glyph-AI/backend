import os
import requests

class SentenceTransformerService():
    def __init__(self):
        self.url = os.getenv("EMBEDDING_SERVICE", "embedding-service:8001")
        pass

    def get_embedding(self, text: str):
        # returns a list of length 768
        data = {
            "text": text
        }
        resp = requests.post(f"http://{self.url}/embed", json=data)
        return resp.json()["vector"]