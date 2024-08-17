import torch
import numpy as np
from transformers import CLIPTokenizer, CLIPTextModel
from functools import lru_cache

@lru_cache(maxsize=1)
class TextToEmbeddings():
    def __init__(self):
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")
        self.model = CLIPTextModel.from_pretrained("openai/clip-vit-base-patch32")

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
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        return self.normalize_embedding(embedding)