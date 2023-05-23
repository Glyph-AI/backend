import os
import requests


class SentenceTransformerService():
    def __init__(self):
        self.url = os.getenv("EMBEDDING_SERVICE",
                             "http://embedding-service:8001")
        pass

    def get_embedding(self, text: str):
        # returns a list of length 768
        data = {
            "text": text
        }
        resp = requests.post(f"{self.url}/embed", json=data)
        return resp.json()["vector"]
