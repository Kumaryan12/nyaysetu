# NyayaSetu

**NyayaSetu** is a source-grounded legal-aid and public-service grievance assistant designed for Indian citizens. It combines fine-tuned NLP classifiers, retrieval-augmented generation, official-source document retrieval, Groq-based answer generation, and safety guardrails.

The goal is to help users understand where their issue belongs, how urgent it may be, what next steps they can take, and which official sources support the response.

> NyayaSetu is not a lawyer and does not provide personal legal advice. It provides general legal/public-service information based on retrieved sources.

---

## Key Features

- Fine-tuned **XLM-RoBERTa issue classifier**
- Fine-tuned **XLM-RoBERTa urgency classifier**
- Rule-based fallback classifiers
- Category correction rules for known high-risk/boundary cases
- Urgency safety correction rules
- RAG pipeline over official-source legal/public-service documents
- ChromaDB vector store
- Multilingual embedding model for future Indian-language support
- Groq LLM answer generation
- Answer guardrails to reduce hallucination and overconfident legal claims
- Source-backed responses
- Next.js frontend chat UI
- Developer/debug panel showing classifier decisions, correction rules, and source retrieval scores

---

## System Architecture

```text
User Query
   ↓
Frontend Chat UI
   ↓
FastAPI Backend
   ↓
Fine-tuned Issue Classifier
   ↓
Fine-tuned Urgency Classifier
   ↓
Correction Rules
   ↓
RAG Retrieval from Official-Source Documents
   ↓
Groq LLM Answer Generation
   ↓
Answer Guardrails
   ↓
Structured Response + Sources
   ↓
Frontend Display + Debug Panel
```

Detailed architecture is available in:

```text
docs/architecture.md
```

---

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- Sentence Transformers
- ChromaDB
- Groq API
- PyPDF

### Machine Learning

- XLM-RoBERTa
- Hugging Face Transformers
- PyTorch
- Scikit-learn
- Pandas
- Datasets

### Frontend

- Next.js
- TypeScript
- Tailwind CSS

---

## Project Structure

```text
nyayasetu/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── services/
│   │   ├── models/
│   │   └── data/
│   │
│   ├── scripts/
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   ├── lib/
│   └── package.json
│
├── ml/
│   ├── datasets/
│   ├── training/
│   └── saved_models/
│
├── docs/
│   ├── architecture.md
│   ├── model_evaluation.md
│   ├── setup.md
│   └── resume_points.md
│
├── .gitignore
└── README.md
```

---

## Main Backend Routes

```text
GET  /health
GET  /chat/classifier-status
POST /chat
POST /chat/debug
```

### `/chat`

Main user-facing endpoint.

Input:

```json
{
  "message": "My employer has not paid my salary for three months. What should I do?"
}
```

Output includes:

```json
{
  "category": "Labour Dispute",
  "urgency": "Medium",
  "simple_answer": "...",
  "next_steps": ["..."],
  "documents_or_details_needed": ["..."],
  "sources": ["..."]
}
```

### `/chat/debug`

Developer/debug endpoint.

Shows:

- ML issue prediction
- Rule-based issue prediction
- Category correction rules applied
- ML urgency prediction
- Rule-based urgency prediction
- Urgency correction rules applied
- Retrieved source scores

This endpoint is useful for development and demos, but should be hidden or protected in production.

---

## Issue Categories

The issue classifier predicts one of the following:

```text
Labour Dispute
Consumer Complaint
Legal Aid
Police Complaint
Domestic Violence / Safety
Municipal Issue
Healthcare Access
Government Scheme
Property Issue
Public Grievance
Unknown
```

---

## Urgency Labels

The urgency classifier predicts:

```text
Low
Medium
High
Unknown
```

Examples:

```text
High:
Immediate danger, violence, missing person, private photo threats, medical emergency.

Medium:
Unpaid salary, refund issue, delayed passport verification, pension delay, eviction notice.

Low:
Information-seeking queries such as "how to apply" or "what documents are needed".

Unknown:
Non-legal or unrelated queries.
```

---

## Model Evaluation

The issue classifier was evaluated on unseen hard Indian grievance-style queries.

Current representative result:

```text
Issue Classifier:
Accuracy: 0.90
Macro F1: 0.89
Weighted F1: 0.89
```

The urgency classifier was evaluated on unseen urgency examples.

Current representative result:

```text
Urgency Classifier:
Accuracy: 0.90
Macro F1: 0.90
Weighted F1: 0.90
```

These results are based on curated and synthetic datasets. They should not be treated as proof of production-level reliability. More real-world data and human evaluation are required before public deployment.

---

## RAG Knowledge Base

Official-source documents are stored in:

```text
backend/app/data/official_docs/
```

Each document can have a metadata file:

```text
document_name.metadata.json
```

Example metadata:

```json
{
  "title": "National Consumer Helpline Basic Information",
  "source_type": "official_website_summary",
  "url": "https://consumerhelpline.gov.in/",
  "jurisdiction": "India",
  "publisher": "Department of Consumer Affairs, Government of India",
  "last_checked": "2026-06-22"
}
```

The RAG pipeline:

```text
Documents
   ↓
Load and clean text
   ↓
Chunk documents
   ↓
Generate embeddings
   ↓
Store in ChromaDB
   ↓
Retrieve relevant chunks
   ↓
Generate answer with Groq
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/nyayasetu.git
cd nyayasetu
```

---

### 2. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```env
APP_NAME=NyayaSetu
APP_ENV=development
APP_DEBUG=true

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions

CHROMA_DB_PATH=app/data/vector_db
CHROMA_COLLECTION_NAME=nyayasetu_legal_docs

EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-base

RAG_TOP_K=5
RAG_MIN_SCORE=0.20
```

Run backend:

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

---

### 3. Prepare RAG index

From inside `backend/`:

```bash
python scripts/prepare_chunks.py
python scripts/build_vector_index.py
```

---

### 4. Frontend setup

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:3000
```

---

## ML Training

### Issue classifier

From project root:

```bash
python ml/training/generate_issue_dataset.py
python ml/training/split_issue_dataset.py
python ml/training/train_issue_classifier.py
```

Evaluate:

```bash
python ml/training/evaluate_issue_file.py --csv ml/datasets/issue_classification_unseen_hard_v3.csv
```

---

### Urgency classifier

From project root:

```bash
python ml/training/generate_urgency_dataset.py
python ml/training/split_urgency_dataset.py
python ml/training/train_urgency_classifier.py
```

Evaluate:

```bash
python ml/training/evaluate_urgency_file.py --csv ml/datasets/urgency_unseen_hard_test.csv
```

---

## Important Git Notes

Do not commit:

```text
backend/.env
frontend/node_modules/
frontend/.next/
ml/saved_models/
backend/app/data/vector_db/
backend/app/data/processed/chunks.jsonl
```

Model weights and vector DB files can be regenerated locally.

---

## Current Limitations

- The official document knowledge base is still small.
- Some current documents are official-source summaries, not full raw official PDFs/pages.
- Classifiers are trained mainly on synthetic and curated data.
- Some real user issues are multi-label, but the current classifier is single-label.
- Speech input is not yet integrated.
- Multilingual response generation is not yet complete.
- The debug panel is for development and demos, not public users.
- The system does not replace lawyers or official authorities.

---

## Future Improvements

- Add full official PDFs and webpages.
- Add state-specific legal/public-service documents.
- Add multilingual speech-to-text.
- Add Hindi/Hinglish response support.
- Add complaint draft generation.
- Add multi-label classification.
- Add admin dashboard.
- Add model calibration and confidence thresholds.
- Add user feedback loop.
- Add Docker-based deployment.
- Add real-world human evaluation.

---

## Resume Summary

Built NyayaSetu, a source-grounded legal-aid and public-service grievance assistant for Indian citizens using fine-tuned XLM-RoBERTa issue and urgency classifiers, RAG over official-source documents, ChromaDB retrieval, Groq-based answer generation, correction rules, safety guardrails, and a Next.js explainability dashboard.