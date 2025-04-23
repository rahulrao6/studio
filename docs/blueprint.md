# **App Name**: ContractIQ

## Core Features:

- Document Upload: Upload contract documents for analysis (PDF, DOCX, TXT).
- Risk Analysis: Analyze contract and identify potential risks. The LLM will use a tool to decide when to identify key dates and clauses related to risk.
- Metadata Display: Display key contract metadata such as extracted dates, parties involved, and overall risk score.

## Style Guidelines:

- Primary color: Neutral white or light gray for a clean, professional look.
- Secondary color: Dark blue or deep teal for headings and important text.
- Accent: Green (#28a745) for highlighting detected risks and key terms.
- Use a clear, structured layout with distinct sections for document upload, analysis results, and metadata display.
- Use icons to represent different risk categories, document types, and analysis stages.

## Original User Request:
You are an expert Python architect and full-stack developer. Your task is to build a production-grade “Enhanced Contract Analysis” microservice in Python, following these requirements exactly:

1. **Tech Stack & Structure**  
   - **Language:** Python 3.10+  
   - **Web framework:** FastAPI  
   - **Async server:** Uvicorn (with auto-reload, production logging)  
   - **Dependency management:** Poetry or pip + requirements.txt  
   - **Containerization:** Provide a Dockerfile and docker-compose.yaml for service + optional Redis for caching/vector DB.  
   - **Project layout:**  
     ```
     contract_service/
     ├── app/
     │   ├── main.py              # FastAPI app factory
     │   ├── config.py            # pydantic-based settings from env
     │   ├── models/              # Pydantic request/response schemas
     │   ├── agents/              # preprocessing, risk, summarization, retrieval modules
     │   ├── security.py          # PII redaction + optional encryption
     │   ├── ml/                  # CAUD dataset integration & model loader
     │   ├── utils/               # helpers (logging, text cleaning)
     │   └── tests/               # pytest test files
     ├── Dockerfile
     ├── docker-compose.yaml
     ├── requirements.txt
     └── README.md
     ```

2. **Configuration & Logging**  
   - All secrets, model paths, feature-flags via environment (use pydantic’s BaseSettings).  
   - Structured JSON logging, configurable log-levels.  

3. **Data Ingestion & Preprocessing**  
   - Accept raw text or file upload (PDF, DOCX, TXT).  
   - Clean/normalize text (Unidecode, whitespace, nulls).  
   - Segment into paragraphs/sections using regex + spaCy grammar cues.  
   - Extract metadata: file size, pages, word count, detected dates & parties (fine-tuned spaCy on CAUD).  
   - PII detection & redaction (email, SSN, credit-card, phone) with regex; option to encrypt redacted text via Fernet.  

4. **Model Management**  
   - **CAUD-Fine-Tuned Models:**  
     - **Legal-BERT** classifier for nuanced risk detection (transformer-based).  
     - **Sentence-Transformer** embedder for semantic search.  
     - **BART-based** summarizer (fallback to a distilled model if needed).  
     - **LLM Agent** (e.g. GPT-style) wrapped as a service or local API call, also fine-tuned on CAUD for deep Q&A.  
   - Singleton loader class to cache models in memory, auto-move to GPU if available, handle missing-model fallbacks gracefully.  

5. **Core Agents**  
   - **PreprocessingAgent:** cleans text, segments, extracts metadata, redacts/encrypts PII, indexes embeddings in FAISS (or Redis-Vector).  
   - **RiskAnalysisAgent:**  
     - Rule-based regex detectors for standard risk patterns.  
     - Transformer inference using CAUD-fine-tuned Legal-BERT to score custom risk categories.  
     - Merge rule-based + transformer outputs; compute per-clause confidence & overall risk score.  
   - **SummarizationAgent:**  
     - Section-level & end-to-end summarization via BART.  
     - Extract key points (dates, payments, terms) with regex+spaCy.  
     - Compute readability (Flesch-Kincaid or custom).  
   - **RetrievalAgent:** semantic similarity search against FAISS index; return top-N similar contracts.  
   - **LLMAgent:** plain-language explanations, follow-up Q&A, revision suggestions—called after risk + summary for “deep dive” responses.

6. **API Endpoints**  
   - `POST /api/analyze` — multipart/form or JSON: triggers ingestion → async-gather(summary, risk, retrieval) → optional LLMAgent refinement → unified JSON response matching a well-documented Pydantic schema.  
   - `POST /api/upload` — file ingest + background indexing  
   - `GET /api/contract/{id}` — fetch cached raw/redacted text + metadata  
   - `POST /api/contract/{id}/section/{sect}/analyze` — section-level analysis (summary, risk, retrieval)  
   - `GET /api/health` — component health (models, disk, DB)  
   - `POST /api/feedback` — collect user feedback, log to structured store  

7. **Reliability & Observability**  
   - Timeout controls, exception handling with clear HTTP codes.  
   - Metrics: processing times per component, request IDs included in logs and responses.  
   - Unit tests + integration tests (pytest + HTTPX).  
   - CI/CD pipeline hints for GitHub Actions: lint (flake8), type-check (mypy), tests.  

8. **Security & Privacy**  
   - CORS locked down or configurable.  
   - PII redaction guaranteed—never return raw PII.  
   - If `ENCRYPTION_ENABLED`, all stored/texts encrypted at rest.  

9. **Performance**  
   - Use async thread-pool for blocking model calls.  
   - Batch requests where possible.  
   - FAISS index kept in memory, flush to disk on shutdown or interval.  

10. **Documentation**  
    - Auto-generate OpenAPI docs, include example payloads.  
    - README with setup, Docker, env vars, usage examples.  

**Deliverable:**  
- A complete, runnable repository as per above layout.  
- Clear inline comments and docstrings.  
- Comprehensive test suite achieving ≥80% coverage.  
- Dockerized service that spins up with a single `docker-compose up`.  

Begin by scaffolding the project structure, then implement each module in turn, following best practices for clean code, dependency injection, and security. Ensure all feature-flags (semantic search, advanced risk, PII detection) are togglable at runtime via configuration.
  