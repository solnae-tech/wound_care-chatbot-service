from app.db.vector_store import VectorStore
from app.utils.embeddings import embed_text

store = VectorStore()
store.load()

def retrieve(query: str):
    """Retrieve relevant information from vector store"""
    if not query or not query.strip():
        return "No specific care instructions available."
    
    try:
        emb = embed_text(query)
        results = store.search(emb, k=2)
        
        if not results:
            return "General wound care: Keep clean, apply antiseptic, and monitor for signs of infection."
        
        return "\n".join(results)
    except Exception as e:
        print(f"RAG retrieval error: {e}")
        return "General wound care: Keep clean and dry."