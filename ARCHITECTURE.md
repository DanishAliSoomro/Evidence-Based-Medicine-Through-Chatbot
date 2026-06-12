# EBM-Connection — System Architecture

## Overview

EBM-Connection is a medical evidence retrieval system built on **GraphRAG** (Graph Retrieval-Augmented Generation). It ingests PMC (PubMed Central) research articles, builds a knowledge graph from them, and exposes a chat interface where users can query medical literature using natural language.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User (Browser)                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  React Frontend  (port 8080)                     │
│              Vite dev server — proxies /api/* to :8000           │
└─────────────────────────┬───────────────────────────────────────┘
                          │ REST /api/*
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│               FastAPI Backend  (port 8000)                       │
│                                                                  │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │ chat.py    │  │  ingest.py   │  │       health.py         │  │
│  │ (sessions, │  │ (PMC PDF     │  │    GET /api/health      │  │
│  │  messages, │  │  ingestion)  │  └─────────────────────────┘  │
│  │  users)    │  └──────┬───────┘                               │
│  └─────┬──────┘         │                                        │
│        │                │                                        │
│        ▼                ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Services Layer                         │    │
│  │  GraphRAGService · PDFProcessingService                  │    │
│  │  GraphRelationExtractor · TextChunker · PMCIngestion     │    │
│  └───────────────┬─────────────────────┬────────────────────┘    │
│                  │                     │                          │
└──────────────────┼─────────────────────┼──────────────────────────┘
                   │                     │
         ┌─────────▼──────┐   ┌──────────▼──────────┐
         │   Neo4j Graph  │   │  SQLite (Relational) │
         │   Database     │   │  medical_rag.db      │
         │  (port 7687)   │   └─────────────────────┘
         └────────────────┘
                   │
         ┌─────────▼──────────┐
         │  Azure OpenAI API  │
         │  gpt-4.1-mini      │
         └────────────────────┘
```

---

## Technology Stack

### Backend
| Layer | Technology | Purpose |
|---|---|---|
| Web Framework | FastAPI | REST API, background tasks, CORS |
| ORM | SQLAlchemy 2.0 (async) | SQLite access |
| Graph DB Client | neo4j (Python driver) | Neo4j read/write |
| Embeddings | SentenceTransformer `all-MiniLM-L6-v2` | 384-dim vector embeddings |
| LLM | Azure OpenAI `gpt-4.1-mini` | Response generation, entity extraction |
| PDF Extraction | PyMuPDF (fitz) | Text extraction from PMC PDFs |
| Config | Pydantic Settings + python-dotenv | Environment variable management |
| Server | Uvicorn | ASGI server |

### Frontend
| Layer | Technology | Purpose |
|---|---|---|
| UI Framework | React 18 | Component-based UI |
| Build Tool | Vite 5 | Dev server, bundling, API proxy |
| Routing | React Router v6 | Client-side navigation |
| Styling | Tailwind CSS + shadcn/ui | Design system |
| Forms | React Hook Form + Zod | Form state and validation |
| HTTP Client | Native `fetch` | API calls via `chatApi.js` |

### Databases
| Database | Type | Purpose |
|---|---|---|
| Neo4j | Graph DB | Knowledge graph (chunks, entities, relationships) |
| SQLite (`medical_rag.db`) | Relational | Users, chat sessions, messages |
| SQLite (`ingestion_checkpoint.db`) | Relational | PDF ingestion tracking |

---

## Directory Structure

```
EBM-Connection/
├── main_api.py                      # FastAPI app entry point
├── config.py                        # Pydantic settings (env vars)
├── requirements.txt                 # Python dependencies
├── .env                             # Secrets (Azure, Neo4j)
├── medical_rag.db                   # SQLite chat/user database
├── ingestion_checkpoint.db          # Ingestion state tracking
├── ingest_pmc.py                    # CLI script for batch ingestion
│
├── api/
│   ├── database.py                  # SQLAlchemy async engine setup
│   ├── models.py                    # ORM models (User, Session, Message)
│   ├── schemas.py                   # Pydantic request/response schemas
│   ├── routes/
│   │   ├── chat.py                  # Users, sessions, messages, chat endpoints
│   │   ├── health.py                # GET /api/health
│   │   └── ingest.py                # PMC ingestion trigger + status
│   ├── services/
│   │   ├── graph_rag_service.py     # Core RAG orchestrator
│   │   ├── graph_extractor.py       # LLM entity/relationship extraction
│   │   ├── pdf_processing_service.py# Full PDF → graph pipeline
│   │   ├── pdf_extractor.py         # PyMuPDF text extraction
│   │   ├── text_chunker.py          # Chunking + embedding generation
│   │   ├── pmc_ingestion_service.py # Batch PMC folder ingestion
│   │   └── prompts.py               # LLM prompt templates
│   ├── repositories/
│   │   ├── neo4j_repsitory.py       # Neo4j queries (store + retrieve)
│   │   └── chat_history_repo.py     # SQLite chat history queries
│   └── utils/
│       ├── text_cleaning.py         # PDF text normalization
│       └── parse_plaintext.py       # Entity/relationship output parsing
│
└── Chat-Design/EBM Frontend/        # React frontend
    ├── vite.config.js               # Proxy: /api/* → localhost:8000
    └── src/
        ├── App.jsx                  # Router + providers
        ├── api/chatApi.js           # All API call functions
        ├── pages/                   # Route-level page components
        ├── components/              # Shared UI components
        ├── hooks/                   # Custom React hooks
        └── lib/utils.js             # Utility helpers
```

---

## Database Schemas

### SQLite — `medical_rag.db`

```
users
├── id          INTEGER PRIMARY KEY
├── username    TEXT UNIQUE
├── email       TEXT UNIQUE
└── password    TEXT (hashed)

chat_sessions
├── id          INTEGER PRIMARY KEY
├── owner_id    INTEGER → users.id
├── title       TEXT
├── created_at  DATETIME
└── is_deleted  BOOLEAN

chat_messages
├── id          INTEGER PRIMARY KEY
├── session_id  INTEGER → chat_sessions.id
├── role        TEXT  ("user" | "assistant")
├── content     TEXT
└── timestamp   DATETIME
```

### Neo4j — Knowledge Graph

```
Nodes:
  (:Chunk)
  ├── chunk_id      STRING (unique)
  ├── text          STRING
  ├── source        STRING (PDF filename)
  ├── page          INTEGER
  └── embedding     FLOAT[] (384 dimensions)

  (:Entity)
  ├── name          STRING (unique, fuzzy-deduplicated)
  └── type          STRING (disease | drug | symptom | treatment | etc.)

Relationships:
  (:Chunk)-[:MENTIONS]->(:Entity)
  (:Entity)-[:RELATED_TO {strength: FLOAT}]->(:Entity)

Indexes:
  Vector index on Chunk.embedding  (cosine similarity)
  Full-text index on Entity.name   (fuzzy search)
```

---

## API Endpoints

### Health
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |

### Users & Auth
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/users` | List all users |
| `POST` | `/api/users` | Register new user |
| `POST` | `/api/login` | Login (username or email + password) |

### Chat Sessions
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/sessions?owner_id=X` | List sessions for a user |
| `POST` | `/api/sessions` | Create new session |
| `GET` | `/api/sessions/:id` | Get session with messages |
| `PATCH` | `/api/sessions/:id` | Rename session |
| `DELETE` | `/api/sessions/:id` | Delete session |
| `GET` | `/api/sessions/:id/messages` | Get all messages in session |

### Chat (Core)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Send query → get AI response |

**Request body:**
```json
{
  "query": "What is the recommended treatment for Type 2 diabetes?",
  "session_id": 123,
  "owner_id": 456
}
```
**Response:**
```json
{
  "session_id": 123,
  "answer": "Based on the evidence..."
}
```

### Ingestion
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/ingest/pmc` | Start background PMC ingestion |
| `GET` | `/api/ingest/pmc/status` | Check ingestion progress |

---

## Core Data Flows

### 1. Chat Query Flow

```
User types query
      │
      ▼
POST /api/chat
      │
      ▼
GraphRAGService
  ├── 1. Embed query          → SentenceTransformer (384-dim vector)
  ├── 2. Vector search        → Neo4j cosine similarity on Chunk.embedding
  ├── 3. Graph traversal      → Expand via Entity → RELATED_TO → Entity
  ├── 4. Context fusion       → Merge text chunks + entities + relationships
  └── 5. LLM generation       → Azure OpenAI (prompt + conversation history)
      │
      ▼
Store user message + assistant response in SQLite
      │
      ▼
Return { session_id, answer } to frontend
```

### 2. PDF Ingestion Flow

```
PMC PDF Files
      │
      ▼
PDFExtractor (PyMuPDF)       → Raw text per page
      │
      ▼
TextCleaner                  → Remove citations ([n]), normalize whitespace
      │
      ▼
TextChunker                  → Overlapping chunks (1000 chars, 100 overlap)
                               + SentenceTransformer embeddings per chunk
      │
      ▼
GraphRelationExtractor (LLM) → Extract entities + relationships per chunk
      │
      ▼
Neo4jRepository
  ├── Store Chunk nodes with embeddings
  ├── Store Entity nodes (fuzzy dedup by name)
  ├── Create MENTIONS edges (Chunk → Entity)
  └── Create RELATED_TO edges (Entity → Entity)
      │
      ▼
Checkpoint DB                → Mark file as ingested (fingerprint + status)
```

### 3. Authentication Flow

```
User submits login form
      │
      ▼
POST /api/login { identifier, password }
      │
      ▼
Backend validates → returns user object
      │
      ▼
Frontend stores user in localStorage (use-auth.js hook)
      │
      ▼
Protected routes check localStorage → redirect to /login if absent
```

---

## Frontend Pages & Routes

| Route | Page | Description |
|---|---|---|
| `/` | `Index.jsx` | Main chat interface (auth required) |
| `/chat/:sessionId` | `Index.jsx` | Load specific conversation |
| `/login` | `Login.jsx` | Login form |
| `/signup` | `Signup.jsx` | Registration form |
| `/settings` | `Settings.jsx` | Settings layout |
| `/settings/general` | `General.jsx` | Theme, language, font size |
| `/settings/chat` | `Chat.jsx` | Export and clear conversations |
| `/settings/datacontrol` | `DataControl.jsx` | API key management |
| `/settings/account` | `Account.jsx` | Username, email, account deletion |
| `*` | `NotFound.jsx` | 404 catch-all |

---

## Configuration & Environment

All secrets are loaded from `.env` via Pydantic Settings:

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_KEY=...
AZURE_DEPLOYMENT_NAME=gpt-4.1-mini

# Neo4j
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
NEO4J_DATABASE=neo4j

# SQLite
DATABASE_URL=sqlite+aiosqlite:///./medical_rag.db
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **GraphRAG over plain RAG** | Entity relationships allow contextual expansion beyond raw vector similarity — better for medical evidence where concepts are interconnected |
| **Neo4j for graph + vectors** | Single store for both vector search (embeddings) and graph traversal (entities/relationships) reduces infrastructure complexity |
| **SQLite for chat history** | Lightweight relational store sufficient for user/session/message data; no separate DB server needed |
| **Azure OpenAI** | Used for both response generation (gpt-4.1-mini) and entity extraction from PDF chunks |
| **SentenceTransformer local** | Embeddings generated locally (no API cost per chunk); 384-dim `all-MiniLM-L6-v2` is fast and sufficient for semantic search |
| **Vite proxy in dev** | Frontend dev server on :8080 proxies `/api/*` to backend :8000, avoiding CORS issues in development |
| **Background tasks for ingestion** | PDF ingestion is slow (LLM calls per chunk); FastAPI BackgroundTasks keeps the HTTP response immediate |

---

## Startup

### Backend
```bash
uvicorn main_api:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (dev)
```bash
cd "Chat-Design/EBM Frontend"
npm run dev        # Starts on http://localhost:8080
```

### PDF Ingestion (CLI)
```bash
python ingest_pmc.py   # Processes PMC articles from ../../PMC-articles
```
