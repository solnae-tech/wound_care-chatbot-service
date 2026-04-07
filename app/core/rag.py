from app.db.vector_store import VectorStore
from app.utils.embeddings import embed_text

store = VectorStore()
store.load()

def retrieve(query: str):
    emb = embed_text(query)
    results = store.search(emb, k=2)
    return "\n".join(results)