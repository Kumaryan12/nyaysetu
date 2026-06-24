# NyayaSetu Architecture

NyayaSetu is a source-grounded legal-aid and public-service grievance assistant designed for Indian citizens. It combines fine-tuned NLP classifiers, retrieval-augmented generation, official-source document retrieval, Groq-based answer generation, and safety guardrails.

The system is not designed to replace a lawyer. It provides general legal and public-service information, suggests next steps, and shows source-backed references.

---

## 1. High-Level System Flow

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