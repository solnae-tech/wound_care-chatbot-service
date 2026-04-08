from app.utils.embeddings import embed_text
from app.db.vector_store import VectorStore

def build_db():
    store = VectorStore()

    data = [
        "Minor cuts: Clean with water, apply antiseptic, cover with bandage. Use paracetamol for pain.",
        "Small wounds: Keep clean and dry. Apply antibiotic ointment if needed.",
        "Mild swelling: Apply cold compress and rest the affected area.",
        "Minor burns: Cool under running water and apply soothing gel.",
    ]

    for text in data:
        emb = embed_text(text)
        store.add(text, emb)

    store.save()
    print("Vector DB created")

if __name__ == "__main__":
    build_db()