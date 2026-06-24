# NyayaSetu

## TL;DR

**NyayaSetu** is a full-stack, source-grounded legal-aid and public-service grievance assistant for Indian citizens.

It combines:

- Fine-tuned **XLM-RoBERTa issue classification**
- Fine-tuned **XLM-RoBERTa urgency classification**
- Official-source **RAG retrieval**
- Groq-based LLM answer generation
- Safety/category correction rules
- Answer guardrails
- Source-backed responses
- A Next.js frontend with an explainability/debug panel

The project is designed as a serious ML-RAG system, not just an LLM chatbot wrapper.

---

## Project Overview

Many citizens struggle to understand where to go when they face issues like unpaid wages, consumer fraud, delayed public services, police complaints, domestic violence, or inability to afford legal help.

NyayaSetu helps users by:

1. Understanding the type of issue they are facing.
2. Detecting urgency and safety risk.
3. Retrieving relevant official-source documents.
4. Generating a simple, grounded answer.
5. Suggesting next steps and required documents.
6. Showing the sources used.
7. Providing an explainability panel for development and demos.

> NyayaSetu does **not** replace lawyers, courts, police, government departments, or legal authorities. It provides general legal/public-service information from available official sources.

---

## Key Features

- Fine-tuned multilingual issue classifier
- Fine-tuned urgency classifier
- Rule-based fallback classifiers
- Category correction rules for known boundary cases
- Safety escalation rules for high-risk situations
- RAG pipeline over official government/legal-aid sources
- Raw-to-clean-to-RAG corpus pipeline
- ChromaDB vector search
- Groq LLM answer generation
- Guardrails against unsupported legal claims
- Source-backed structured responses
- Developer debug panel
- Retrieval evaluation pipeline
- RAG document audit pipeline
- Hugging Face model hosting workflow

---

## Demo Capabilities

Example user query:

```text
My employer has not paid my salary for three months. What should I do?
```

NyayaSetu returns:

- Issue category: `Labour Dispute`
- Urgency: `Medium`
- Simple explanation
- Suggested next steps
- Documents/details needed
- Relevant official sources

Example safety query:

```text
Loan app is sending my photos to contacts.
```

NyayaSetu can identify this as a high-risk situation and escalate urgency using safety correction rules.

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
RAG Retrieval from Official Sources
   ↓
Groq LLM Answer Generation
   ↓
Answer Guardrails
   ↓
Structured Response + Sources
   ↓
Frontend Display + Debug Panel
```

---

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- ChromaDB
- Sentence Transformers
- Groq API
- PyTorch
- Hugging Face Transformers

### Machine Learning

- XLM-RoBERTa
- Hugging Face Trainer
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
│   │   ├── models/
│   │   ├── services/
│   │   └── data/
│   │       ├── source_registry/
│   │       ├── official_docs_raw/
│   │       ├── official_docs_clean/
│   │       ├── manual_docs/
│   │       ├── rag_docs/
│   │       ├── processed/
│   │       ├── eval/
│   │       └── vector_db/
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
├── README.md
└── .gitignore
```

---

## Backend Routes

```text
GET  /health
GET  /chat/classifier-status
POST /chat
POST /chat/debug
```

### `POST /chat`

Main user-facing endpoint.

Example request:

```json
{
  "message": "My employer has not paid my salary for three months. What should I do?"
}
```

Example response fields:

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

### `POST /chat/debug`

Developer/demo endpoint.

Shows:

- ML issue prediction
- Rule-based issue prediction
- Category correction result
- ML urgency prediction
- Rule-based urgency prediction
- Urgency correction result
- Retrieved source scores

This endpoint is useful for demos and debugging, but should be hidden or protected in production.

---

## Issue Classification

NyayaSetu uses a fine-tuned XLM-RoBERTa classifier for issue categorization.

### Labels

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

The classifier is designed for Indian grievance-style queries, including:

- English
- Hinglish
- Roman Hindi
- Broken English
- Speech-like short queries
- Informal complaint phrasing

---

## Urgency Classification

NyayaSetu also uses a fine-tuned XLM-RoBERTa urgency classifier.

### Labels

```text
Low
Medium
High
Unknown
```

### Meaning

```text
High:
Immediate danger, violence, missing person, medical emergency, private-image threats, forced confinement, stalking.

Medium:
Important but not immediately life-threatening issues such as unpaid salary, refund denial, delayed documents, pension delay, eviction notice.

Low:
Information-seeking queries such as how to apply, where to complain, or what documents are needed.

Unknown:
Unrelated or non-legal queries.
```

---

## Classifier Evaluation

### Issue Classifier

Evaluated on unseen hard Indian grievance-style queries.

```text
Accuracy:    0.90
Macro F1:    0.89
Weighted F1: 0.89
```

### Urgency Classifier

Evaluated on unseen urgency examples.

```text
Accuracy:    0.90
Macro F1:    0.90
Weighted F1: 0.90
```

These results are from curated/synthetic evaluation sets and should not be treated as production-level reliability. More real-world data and human evaluation are needed before public deployment.

---

## RAG Corpus Pipeline

NyayaSetu uses a raw-to-clean-to-final corpus pipeline for RAG.

```text
official_docs_raw/
   ↓
official_docs_clean/
   ↓
manual_docs/
   ↓
rag_docs/
   ↓
processed/chunks.jsonl
   ↓
vector_db/
```

### Folder Roles

| Folder | Purpose |
|---|---|
| `official_docs_raw/` | Untouched scraped official webpage text |
| `official_docs_clean/` | Cleaned official webpage content |
| `manual_docs/` | Curated official-source summaries |
| `rag_docs/` | Final RAG-ready corpus |
| `processed/` | Generated chunks |
| `vector_db/` | ChromaDB index |

---

## RAG Document Quality

The RAG corpus is built from official or official-source documents.

Current included sectors:

- Legal Aid
- Consumer Complaint
- Police Complaint
- Public Grievance
- Domestic Violence / Safety

The cleaning pipeline removes:

- Navigation menus
- Footer text
- Accessibility boilerplate
- Repeated lines
- Broken tables
- Irrelevant webpage UI text

The audit script checks:

- Word count
- Metadata completeness
- Missing title/source/domain/publisher fields
- Noisy webpage patterns
- Broken table patterns
- Repeated lines

---

## RAG Retrieval Evaluation

Retrieval is evaluated using a curated query set across multiple domains.

Metrics used:

| Metric | Meaning |
|---|---|
| Domain Recall@1 | Whether the top result belongs to the expected domain |
| Domain Recall@3 | Whether any top-3 result belongs to the expected domain |
| Source Recall@5 | Whether the expected official source appears in the top 5 |
| MRR | Mean Reciprocal Rank of the first expected source |

### Current Retrieval Results

On a curated 24-query retrieval evaluation set:

```text
Domain Recall@1: 1.000
Domain Recall@3: 1.000
Source Recall@5: 1.000
MRR:             0.979
```

These results show that the current RAG database retrieves the correct official source for the tested queries. The evaluation set is still limited and should be expanded before production use.

---

## Example Retrieval Results

### Query

```text
How can I get free legal aid?
```

Top retrieved sources:

```text
1. NALSA FAQs — Legal Aid
2. NALSA FAQs — Legal Aid
3. NALSA FAQs — Legal Aid
```

### Query

```text
My online order was defective and seller is not refunding
```

Top retrieved sources:

```text
1. National Consumer Helpline Contact — Consumer Complaint
2. National Consumer Helpline About — Consumer Complaint
3. National Consumer Helpline — Consumer Complaint
```

### Query

```text
How can I get FIR copy?
```

Top retrieved sources:

```text
1. Digital Police Citizen Services — Police Complaint
2. Digital Police CCTNS About — Police Complaint
3. Digital Police CCTNS About — Police Complaint
```

### Query

```text
Can I appeal if my CPGRAMS grievance is closed?
```

Top retrieved sources:

```text
1. CPGRAMS Public Grievance Portal — Public Grievance
2. CPGRAMS Lodge Grievance — Public Grievance
3. NALSA FAQs — Legal Aid
```

---

## Groq LLM Usage

Groq is used for answer generation only.

The LLM receives:

- User query
- Retrieved source snippets
- Strict prompt instructions
- JSON output format requirements

The LLM is instructed to:

- Use only retrieved sources
- Avoid pretending to be a lawyer
- Avoid inventing legal sections, deadlines, phone numbers, or procedures
- Say when sources are insufficient
- Return a structured response

---

## Guardrails

NyayaSetu applies answer guardrails after LLM generation.

Guardrails reduce the risk of:

- Unsupported legal claims
- Overconfident advice
- Hallucinated deadlines
- Hallucinated legal sections
- Unsupported emergency guidance

If sources are weak or missing, the system responds with a fallback message instead of inventing an answer.

---

## Explainability / Debug Panel

The frontend includes a developer/debug panel showing:

- ML issue classifier output
- ML urgency classifier output
- Rule-based predictions
- Correction rules applied
- Final category
- Final urgency
- Retrieved source scores

This makes the system easier to debug and demonstrate.

Example:

```text
Input: loan app is sending my photos to contacts

ML urgency prediction: Medium
Urgency correction rule: high_risk_safety_pattern
Final urgency: High
```

---

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/nyayasetu.git
cd nyayasetu
```

---

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create:

```text
backend/.env
```

Example:

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

Backend:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

---

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

## Fine-Tuned Model Weights

The fine-tuned model weights are **not stored in this GitHub repository** because they are large.

They should be downloaded separately from Hugging Face.

### Download Models

Install Hugging Face Hub CLI:

```bash
pip install -U huggingface_hub
```

Login:

```bash
hf auth login
```

Download issue classifier:

```bash
mkdir -p ml/saved_models

hf download kumaryan12/nyayasetu-issue-classifier-xlm-r \
  --local-dir ml/saved_models/issue_classifier_xlmr
```

Download urgency classifier:

```bash
hf download kumaryan12/nyayasetu-urgency-classifier-xlm-r \
  --local-dir ml/saved_models/urgency_classifier_xlmr
```

Expected local folders:

```text
ml/saved_models/issue_classifier_xlmr/
ml/saved_models/urgency_classifier_xlmr/
```

Each should contain:

```text
config.json
model.safetensors
tokenizer.json
tokenizer_config.json
sentencepiece.bpe.model
special_tokens_map.json
```

If these folders are missing, the backend will fall back to rule-based classification.

---

## Build RAG Database

From inside `backend/`:

```bash
python scripts/ingest_official_webpages.py
python scripts/build_clean_official_docs.py
python scripts/build_rag_corpus.py
python scripts/audit_rag_docs.py
python scripts/prepare_chunks.py
python scripts/build_vector_index.py
python scripts/evaluate_retrieval.py
```

Pipeline summary:

```text
ingest_official_webpages.py      -> official_docs_raw/
build_clean_official_docs.py     -> official_docs_clean/
build_rag_corpus.py              -> rag_docs/
audit_rag_docs.py                -> quality audit
prepare_chunks.py                -> processed/chunks.jsonl
build_vector_index.py            -> ChromaDB vector index
evaluate_retrieval.py            -> retrieval metrics
```

---

## ML Training

### Issue Classifier

```bash
python ml/training/generate_issue_dataset.py
python ml/training/split_issue_dataset.py
python ml/training/train_issue_classifier.py
```

Evaluate:

```bash
python ml/training/evaluate_issue_file.py --csv ml/datasets/issue_classification_unseen_hard_v3.csv
```

### Urgency Classifier

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

## What Is Not Committed

The following files/folders are intentionally excluded:

```text
backend/.env
backend/.venv/
frontend/node_modules/
frontend/.next/
backend/app/data/vector_db/
backend/app/data/processed/chunks.jsonl
backend/app/data/eval/rag_audit_report.json
backend/app/data/eval/retrieval_eval_report.json
ml/saved_models/
ml/**/checkpoint-*
```

These are generated locally or downloaded separately.

---

## Current Limitations

- The RAG corpus is still small.
- The retrieval evaluation set is curated and limited.
- Some domains have fewer sources than others.
- Some official websites are dynamic and difficult to scrape cleanly.
- The classifiers are trained mainly on curated/synthetic examples.
- Current classification is single-label.
- State-specific legal/public-service handling is limited.
- Speech input is not yet integrated.
- Hindi/Hinglish response generation is not fully implemented.
- The system is not suitable for unsupervised production legal advice.

---

## Future Work

- Add more official sources sector by sector.
- Expand retrieval evaluation to 100+ queries.
- Add NCW, cybercrime, labour, healthcare, municipal, RERA, and state-specific sources.
- Add section-aware and FAQ-aware chunking.
- Add multilingual typed Hindi/Hinglish responses.
- Add speech-to-text support.
- Add complaint draft generation.
- Add user feedback loop.
- Add admin review for high-risk cases.
- Add deployment with lightweight model-loading strategy.
- Add model hosting via Hugging Face.
- Add Docker setup.

---

## Disclaimer

NyayaSetu is an educational and research-oriented project. It does not provide legal advice and should not be used as a substitute for lawyers, courts, police, government departments, or official legal services authorities.