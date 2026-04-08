import faiss
import numpy as np
import json
import os

class VectorStore:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.documents = []

    def add(self, text, embedding):
        self.index.add(np.array([embedding]).astype("float32"))
        self.documents.append(text)

    def search(self, query_embedding, k=3):
        """Search for similar documents"""
        # Check if index has any vectors
        if self.index.ntotal == 0:
            return []  # Return empty list if no documents
        
        # Ensure we don't request more results than available
        k = min(k, self.index.ntotal)
        
        D, I = self.index.search(
            np.array([query_embedding]).astype("float32"), k
        )
        
        # Filter out invalid indices
        results = []
        for i in I[0]:
            if 0 <= i < len(self.documents):
                results.append(self.documents[i])
        
        return results

    def save(self, path="data/vector_store.pkl"):
        """Save vector store using safe serialization (JSON + numpy)"""
        base_path = path.replace('.pkl', '')
        
        # Save FAISS index
        faiss.write_index(self.index, f"{base_path}.index")
        
        # Save documents as JSON
        with open(f"{base_path}.json", "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)

    def load(self, path="data/vector_store.pkl"):
        """Load vector store from safe serialization"""
        base_path = path.replace('.pkl', '')
        
        # Load FAISS index
        index_file = f"{base_path}.index"
        json_file = f"{base_path}.json"
        
        if os.path.exists(index_file):
            self.index = faiss.read_index(index_file)
            print(f"Loaded FAISS index: {self.index.ntotal} vectors")
        else:
            print(f"Warning: {index_file} not found, using empty index")
        
        # Load documents from JSON
        if os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
            print(f"Loaded {len(self.documents)} documents")
        else:
            print(f"Warning: {json_file} not found, using empty documents list")