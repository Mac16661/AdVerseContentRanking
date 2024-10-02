import numpy as np
from sentence_transformers import SentenceTransformer
from functools import lru_cache

@lru_cache(maxsize=1)
class TextToEmbeddings():
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Initialized Text Embedding Model ========================================\n")

    def normalize_embedding(embedding):
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm

    def getEmbedding(self, text):
        if isinstance(text, str):
            embeddings = self.model.encode([text])
            return embeddings.tolist()