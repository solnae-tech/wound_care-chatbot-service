import faiss
import numpy as np
import pickle

class VectorStore:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.documents = []

    def add(self, text, embedding):
        self.index.add(np.array([embedding]).astype("float32"))
        self.documents.append(text)

    def search(self, query_embedding, k=3):
        D, I = self.index.search(
            np.array([query_embedding]).astype("float32"), k
        )
        return [self.documents[i] for i in I[0]]

    def save(self, path="data/vector_store.pkl"):
        with open(path, "wb") as f:
            pickle.dump((self.index, self.documents), f)

    def load(self, path="data/vector_store.pkl"):
        with open(path, "rb") as f:
            self.index, self.documents = pickle.load(f)