# 🩺 Medical AI Chatbot (MVP)

An intelligent medical assistant chatbot that combines **Deep Learning (DL)**, **LLM reasoning (Groq)**, and **RAG (Retrieval-Augmented Generation)** to provide safe and context-aware guidance for wound-related conditions.

---

## 🚀 Features

- 🤖 **LLM-based reasoning** using Groq API  
- 🧠 **DL model integration** (infection detection input)  
- 🔍 **Vector database (FAISS)** for medical knowledge retrieval  
- ⚠️ **Severity classification (low / medium / high)**  
- 🛡️ **Rule-based safety overrides**  
- 💬 Structured JSON responses  

---

## 🧠 System Architecture
User Input + DL Output
↓
Chatbot Engine
↓
LLM (Decision Making)
↓
Rule-Based Overrides (Safety)
↓
RAG (for low/medium cases only)
↓
Final JSON Response

---

## 📦 Tech Stack

- **Backend:** FastAPI  
- **LLM:** Groq 
- **Embeddings:** Sentence Transformers  
- **Vector DB:** FAISS  
- **Language:** Python  

---

## 📁 Project Structure
medical_chatbot_mvp/
│
├── app/
│ ├── main.py
│ ├── api/
│ │ └── chat.py
│ ├── core/
│ │ ├── chatbot.py
│ │ ├── rag.py
│ ├── llm/
│ │ └── groq_client.py
│ ├── db/
│ │ ├── vector_store.py
│ │ ├── ingest.py
│ ├── utils/
│ │ └── embeddings.py
│
├── data/
│ └── vector_store.pkl
│
├── requirements.txt
├── .env
└── README.md


---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-link>
cd medical_chatbot_mvp
2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac
3. Install dependencies
pip install -r requirements.txt
4. Add Groq API Key

Create a .env file:

GROQ_API_KEY=your_api_key_here
5. Build Vector Database
python app/db/ingest.py
6. Run the server
uvicorn app.main:app --reload
🧪 API Usage
Endpoint:
POST /chat
Sample Request:
{
  "message": "My wound is slightly swollen and painful",
  "pain_level": 5,
  "discomfort_level": 6,
  "dl_output": {
    "infection_detected": false
  }
}
Sample Response:
{
  "answer": "...Recommended Care...",
  "medical_attention_needed": "no",
  "severity": "medium"
}
🧠 Decision Logic

The system combines:

DL Output → infection detection
User Inputs → pain & discomfort levels
LLM Reasoning → contextual understanding
Rule-Based Overrides → safety-critical decisions
Key Rules:
Pain ≥ 8 → High severity
Infection + pain ≥ 6 → High severity
Moderate symptoms → Medium
Low symptoms → Low
⚠️ Safety Design
🚫 No medical diagnosis
⚠️ High-risk cases → always escalated
🧠 Symptoms can override model predictions
🔍 RAG used only for safe cases
🎯 Demo Highlights
Shows intelligent decision-making
Combines multiple AI techniques
Handles edge cases (e.g., high pain without infection)
Provides safe and explainable outputs
🔮 Future Improvements
Add duration & symptom tracking
Improve medical dataset (RAG)
Frontend chat interface
Doctor/hospital recommendation system