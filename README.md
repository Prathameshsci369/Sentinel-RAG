

<div align="center">
  <h1>🛡️ AegisRAG</h1>
  <p><strong>Enterprise-Grade, Privacy-First Retrieval-Augmented Generation</strong></p>
  <p>100% Local Infrastructure. Zero Cloud Dependencies. Strict Multi-Tenant RBAC.</p>
  
  <img src="https://img.shields.io/badge/FastAPI-0.115.6-0097A7?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PostgreSQL-4.4-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Qdrant-1.12.1-DC2F55?logo=qdrant&logoColor=white" alt="Qdrant">
  <img src="https://img.shields.io/badge/Redis-7.2-DC382D?logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/Celery-5.6.3-37814A?logo=celery&logoColor=white" alt="Celery">
  <img src="https://img.shields.io/badge/LLaMA.cpp-0.11.5-4183D5?logo=llama&logoColor=white" alt="llama.cpp">
</div>

---

## 📖 Overview

**AegisRAG** is a highly scalable, production-ready RAG backend built from the ground up with strict architectural boundaries. In enterprise environments, data privacy is paramount. AegisRAG ensures that **no proprietary data, embeddings, or LLM prompts ever leave the local network**. 

Instead of relying on black-box cloud APIs (OpenAI, Pinecone), this system runs entirely on local hardware using a local LLM (`llama.cpp`), local embedding models (`Sentence-Transformers`), and a native vector database (`Qdrant`).

## 🏗️ Architecture

The project strictly follows a **5-Layered Architecture**, ensuring that business logic never leaks into infrastructure, and infrastructure never leaks into API routes.

1. **API / Dependency Layer:** FastAPI routers and dependency injection (Security guards, Request ID injection).
2. **Service Layer:** The "Brains." Orchestrates use cases, calls repositories, and handles business logic (e.g., RAG pipeline flow).
3. **Repository Layer:** "Translators." Takes Python objects and translates them into raw SQL or Qdrant queries.
4. **Domain Layer:** SQLAlchemy models and Pydantic schemas. Defines the exact shape of the data.
5. **Infrastructure Layer:** "Dumb Pipes." Talks to Postgres, Qdrant, Redis, and local AI models. Contains zero business logic.

## ⚡ Core Features

### 1. Advanced RAG Pipeline (Phase 3)
Moves far beyond naive "embed-and-search" implementations:
*   **Recursive Chunking:** Splits documents logically (paragraphs/sentences) rather than blindly slicing characters.
*   **Hybrid Search:** Combines **Dense Vector Search** (Qdrant) with **Sparse Keyword Search** (Postgres Full-Text Search BM25).
*   **Reciprocal Rank Fusion (RRF):** Pure mathematical implementation to merge the two ranked lists into a single, highly accurate Top 10 list.
*   **Cross-Encoder Reranking:** Uses a specialized NLP model to read the `(Query, Chunk)` pair together, scoring precise relevance to extract the Top 3.

### 2. Strict Enterprise RBAC & Multi-Tenancy
*   Data-Driven Permissions Matrix (No messy `if/else` role checking).
*   **Dual-Layer Security:** 
    *   *Postgres Layer:* SQL filters block unauthorized rows at the database level.
    *   *Vector Layer:* Qdrant Payload Filters block unauthorized embeddings *before* they even reach the LLM.
*   Documents are tagged with `Tenant`, `Department`, and `Visibility` (`GENERAL`, `MANAGEMENT`, `CONFIDENTIAL`).

### 3. Asynchronous Processing & Scaling
*   FastAPI handles API requests instantly.
*   Heavy lifting (PDF parsing, embedding generation, vector upserts) is offloaded to **Celery** workers.
*   Communication handled via **Redis** broker.

### 4. Intelligent Caching
*   **LLM Response Caching:** Hashes `(user_id + query)` and caches the final LLM response in Redis. Identical queries return in milliseconds instead of seconds.
*   **Fail-Open Design:** If Redis crashes, the full RAG pipeline takes over seamlessly.

### 5. Observability & Health
*   **Structured Logging:** Pure JSON logs via `structlog` (ready for Datadog/ELK).
*   **Request Tracing:** Global `X-Request-ID` middleware ties all logs for a single HTTP request together.
*   **Deep Health Checks:** `/health/db`, `/health/redis`, `/health/qdrant`, `/health/llm` endpoints verify actual service connectivity.

### 6. Data Integrity
*   **Soft Deletes:** Records are marked `deleted_at` instead of being purged from the database.
*   **Audit Logging:** Tracks all critical actions (uploads, searches, logins) in a dedicated JSON table.
*   **Prompt Versioning:** LLM prompts stored in JSON config files, allowing hot-swapping of system prompts without code redeployment.

## 📁 Directory Structure

```text
.
├── alembic/                     # Database migrations
│   └── versions/
├── app
│   ├── ai/                       # AI/ML Brains (Plumbing)
│   │   ├── chunking/             # Recursive Character Text Splitter
│   │   ├── embeddings/           # Sentence-Transformers wrapper
│   │   ├── llm/                  # Local LLM client (llama.cpp OpenAI wrapper)
│   │   ├── prompts/              # Versioned LLM prompts (.json)
│   │   └── reranker/             # Cross-Encoder reranking logic
│   ├── core/                      # Global configs, enums, security (bcrypt)
│   ├── dependencies/             # FastAPI dependency injection (Auth, Permissions)
│   ├── infrastructure/           # External systems plumbing
│   │   ├── database/             # SQLAlchemy engine, session, base
│   │   ├── qdrant/              # Qdrant client, dynamic dimension mapping
│   │   └── redis/               # Redis client, locks, caching logic
│   ├── middleware/                # Request ID injection, auth, rate limiting
│   ├── modules/                  # Domain-Driven Bounded Contexts
│   │   ├── audit/                # Audit log models
│   │   ├── departments/          # Tenant department models
│   │   ├── documents/            # Document upload, Hybrid Search, RAG loop
│   │   ├── health/               # Deep infrastructure health checks
│   │   ├── ingestion/            # Celery background task (PDF -> Chunk -> Embed -> Qdrant)
│   │   ├── retrieval/            # (Legacy) Direct Qdrant search
│   │   ├── roles/                # RBAC role definitions
│   │   ├── search/               # (Legacy) Direct RAG endpoints
│   │   ├── tenants/              # Multi-tenant models
│   └── users/                # User models, registration, login
│   ├── workers/                   # Celery app and task definitions
├── deployments/                # Docker and Kubernetes YAMLs
├── docs/                       # ADRs and advanced documentation
├── scripts/                    # DB seeding and utility scripts
├── tests/                      # Unit, integration, e2e tests
├── uploads/                    # Local PDF storage
├── pyproject.toml
└── requirements.txt
```

## 🛠️ Tech Stack

*   **Backend:** FastAPI, Python 3.13, Pydantic v2
*   **Database:** PostgreSQL (psycopg), SQLAlchemy 2.0 (Sync)
*   **Migrations:** Alembic
*   **Queue:** Celery, Redis (Native binary)
*   **Vector DB:** Qdrant (Native server binary)
*   **Embeddings:** `BAAI/bge-small-en-v1.5` (via Sentence-Transformers)
*   **Reranker:** `cross-encoder/ms-marco-MiniLM-L-6-v2`
*   **LLM:** Gemma 2 4B (via `llama.cpp` server)
*   **Auth:** Native `bcrypt`, PyJWT

## 🚀 Local Setup & Execution

Because this is a 100% local stack, you must run 5 separate services. 

### 1. Prerequisites
```bash
pip install -r requirements.txt
```

### 2. Start Infrastructure Services
```bash
# 1. Redis (Background)
redis-server --daemonize yes

# 2. Qdrant Vector DB (Background)
./qdrant &

# 3. LLM Server (e.g., Gemma 2 4B via llama.cpp)
./build/bin/llama-server -m "/path/to/model.gguf" --host 0.0.0.0 --port 8080 --ctx-size 640000
```

### 3. Configure Environment
Copy `.env.example` to `.env` and fill in your Postgres credentials and configuration:
```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=enterprise_rag
DATABASE_USER=enterprise_user
DATABASE_PASSWORD=12345
SECRET_KEY=your-super-secret-key
LLM_BASE_URL=http://localhost:8080/v1
LLM_MODEL_NAME=gemma-2-4b
REDIS_HOST=localhost
REDIS_PORT=6379
QDRANT_URL=http://localhost:6333
```

### 4. Database Migrations
```bash
alembic upgrade head
```

### 5. Start Application Servers
```bash
# Terminal 1: FastAPI
uvicorn app.main:app --reload

# Terminal 2: Celery Worker
celery -A app.workers.celery_app:celery_app worker --loglevel=info
```

### 6. Access API
Navigate to `http://localhost:8000/docs` for interactive Swagger UI. 
Run the user seeding script to create test accounts:
```bash
python scripts/seed_test_users.py
```

## 🛡️ Security Posture

*   **No `passlib`:** Uses native `bcrypt` to avoid Python 3.13 compatibility crashes.
*   **Postgres FTS Safety:** Uses `func.plainto_tsquery()` instead of `.match()` to prevent syntax injection on raw user strings.
*   **Qdrant Server Mode:** Enforces client-server architecture to prevent file-locking deadlocks between FastAPI and Celery workers.
*   **Guard Clauses:** RBAC filters safely return empty lists instead of crashing if a user lacks a tenant assignment.

## 🗺️ Roadmap

- [x] **Project 1: AegisRAG (Current)** - Enterprise RAG with Hybrid Search & RBAC.
- [ ] **Project 2: Research Assistant** - Multi-document reasoning, web search integration.
- [ ] **Project 3: AI SaaS Platform** - API keys, billing, multi-tenant SaaS.
- [ ] **Project 4: Agentic Automation** - LangGraph, tool calling, human-in-the-loop workflows.
- [ ] **Phase 5:** Interview Preparation & Theory deep-dive.

## 📜 License

This project is licensed under the MIT License.
```
