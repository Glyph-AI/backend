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

    def get_batch_embedding(self, text: str, chunk_size=2000, overlap=500):
        data = {
            "chunk_size": chunk_size,
            "overlap": overlap,
            "text": text
        }

        resp = requests.post(f"{self.url}/embed/batch", json=data)
        print(resp.json())
        return resp.json()
