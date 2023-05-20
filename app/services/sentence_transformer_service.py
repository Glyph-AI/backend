from sentence_transformers import SentenceTransformer

class SentenceTransformerService():
    def __init__(self):
        self.model = SentenceTransformer("/embedding_model")
        pass

    def get_embedding(self, text: str):
        # returns a list of length 768
        return self.model.encode(text)