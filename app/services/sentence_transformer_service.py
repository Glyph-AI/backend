from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-mpnet-base-v2")

class SentenceTransformerService():
    def __init__(self):
        pass

    def get_embedding(self, text: str):
        # returns a list of length 768
        return model.encode(text)