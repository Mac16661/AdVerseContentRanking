import numpy as np
from sentence_transformers import SentenceTransformer
from functools import lru_cache

@lru_cache(maxsize=1)
class TextToEmbeddings():
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def normalize_embedding(self, embedding):
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm

    def textToEmbedding(self, text):
        """
            Convert text data into vector embeddings 
            Args:
                text -> text from speech data

            returns:
                vector embeddings
        """
        embeddings = self.model.encode(text)
        print(embeddings)
        #Output: torch.Size([1, 384])
        return self.normalize_embedding(embeddings)