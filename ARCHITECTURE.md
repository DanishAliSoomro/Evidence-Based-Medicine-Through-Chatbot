# EBM-Connection — System Architecture

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (React + Vite)                   │
│                                                                  │
│   ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌────────────┐  │
│   │  Login / │  │  Chat Page │  │ Settings │  │  403 / 404 │  │
│   │  Signup  │  │  (Index)   │  │  Pages   │  │   Pages    │  │
│   └──────────┘  └────────────┘  └──────────┘  └────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │  HTTP + JSON
                         │  Authorization: Bearer <token> on every request
                         │  Vite proxy:  /api  →  localhost:8000
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND  (main_api.py)               │
│                                                                  │
│          Routes  →  Services  →  Repositories  →  Utils         │
└──────┬──────────────────────┬────────────────────────┬──────────┘
       │                      │                        │
       ▼                      ▼                        ▼
┌─────────────┐     ┌──────────────────┐     ┌────────────────────┐
│   SQLite    │     │      Neo4j       │     │  Azure OpenAI      │
│             │     │                  │     │  GPT-4o mini       │
│  users      │     │  Chunks (vectors)│     │                    │
│  sessions   │     │  Entities        │     │  Chat generation   │
│  messages   │     │  Relationships   │     │  Embeddings        │
└─────────────┘     └──────────────────┘     │  Vision (images)   │
                                             │  Classification    │
                                             │  Graph extraction  │
                                             └────────────────────┘
```

---

## Frontend Structure

```
src/
│
├── pages/
│   ├── Index.jsx ──────────────── Main chat page (owns all app state)
│   ├── Login.jsx ──────────────── Email + password sign in
│   ├── Signup.jsx ─────────────── Register → redirects to /login?registered=1
│   ├── NotAuthorized.jsx ──────── 403 page (wrong user accessing a session)
│   ├── NotFound.jsx ───────────── 404 page
│   └── settings/
│       ├── General.jsx ────────── Language toggle (English / Urdu)
│       ├── Chat.jsx
│       ├── Account.jsx
│       └── DataControl.jsx
│
├── components/
│   ├── ChatSidebar.jsx ────────── Session list + New Chat + user dropdown
│   ├── ConversationList.jsx ───── Search bar + session rows + delete
│   ├── ChatMain.jsx ───────────── Welcome screen / message feed + footer
│   ├── ChatInput.jsx ──────────── Textarea, file attach, Ctrl+V paste, send
│   ├── ChatMessage.jsx ────────── Renders message + image lightbox
│   └── CollapsedSidebar.jsx ───── Collapsed sidebar icon bar
│
├── hooks/
│   ├── use-auth.js ────────────── user + JWT token  →  localStorage
│   ├── use-dark-mode.js ───────── dark mode with cross-tab event sync
│   └── use-language.js ────────── en/ur language with cross-tab event sync
│
└── api/
    └── chatApi.js ─────────────── All fetch calls, auto-attaches Bearer token
```

---

## Backend Layer Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         ROUTES LAYER                             │
│               (HTTP boundary — accepts requests)                 │
│                                                                  │
│   auth.py    →  POST /api/users          POST /api/login         │
│   chat.py    →  GET/POST/PATCH/DELETE /api/sessions              │
│                 POST /api/chat                                   │
│   ingest.py  →  POST /api/ingest/pmc    GET /api/ingest/pmc/status│
│   vision.py  →  POST /api/vision/test   POST /api/pdf/test       │
│   health.py  →  GET  /api/health                                 │
└─────────────────────────┬────────────────────────────────────────┘
                          │ calls
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                        SERVICES LAYER                            │
│                (Business logic + orchestration)                  │
│                                                                  │
│   registry.py             auth: hash password, issue JWT         │
│   graph_rag_service.py    4-step GraphRAG pipeline               │
│   pmc_ingestion_service.py  batch PMC folder processing          │
│   pdf_processing_service.py  PDF → chunks → Neo4j               │
│   graph_extractor.py      LLM entity + relationship extraction   │
│   text_chunker.py         split text, compute embeddings         │
│   pdf_extractor.py        PMC PDF files → raw text              │
└─────────────────────────┬────────────────────────────────────────┘
                          │ calls
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                      REPOSITORIES LAYER                          │
│                   (Database commands only)                       │
│                                                                  │
│   chat_history_repo.py   all SQLite reads + writes               │
│   neo4j_repository.py    vector search + graph traversal         │
└─────────────────────────┬────────────────────────────────────────┘
                          │ calls
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                        UTILS LAYER                               │
│                (Pure functions, no side effects)                 │
│                                                                  │
│   security.py        SHA256 hash, JWT encode/decode              │
│   vision.py          image base64  →  text  (GPT-4o mini)        │
│   classifier.py      text  →  medical? high/medium/low           │
│   pdf_extractor.py   PDF bytes  →  plain text  (PyMuPDF)         │
│   parse_plaintext.py parse LLM entity/relationship output        │
│   text_cleaning.py   text normalisation                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

```
┌─────────────────────────────────────────────────────────────────┐
│                           SQLITE                                │
│                        medical_rag.db                           │
│                                                                 │
│  ┌──────────────────────────────────┐                          │
│  │              users               │                          │
│  ├──────────────────────────────────┤                          │
│  │  id             INTEGER   PK     │                          │
│  │  username       STRING           │                          │
│  │  email          STRING    UNIQUE │                          │
│  │  password_hash  STRING           │                          │
│  │  oauth_provider STRING  ◄──────────── defined, not yet      │
│  │  oauth_id       STRING  ◄──────────── implemented           │
│  │  auth_type      STRING  ◄──────────── (dead columns)        │
│  │  created_at     DATETIME         │                          │
│  └────────────────┬─────────────────┘                          │
│                   │ 1                                           │
│                   │ has many                                    │
│                   ▼ N                                           │
│  ┌──────────────────────────────────┐                          │
│  │           chat_sessions          │                          │
│  ├──────────────────────────────────┤                          │
│  │  id          INTEGER   PK        │                          │
│  │  user_id     INTEGER   FK ───────────► users.id             │
│  │  title       STRING              │                          │
│  │  created_at  DATETIME            │                          │
│  └────────────────┬─────────────────┘                          │
│                   │ 1                                           │
│                   │ has many                                    │
│                   ▼ N                                           │
│  ┌──────────────────────────────────┐                          │
│  │           chat_messages          │                          │
│  ├──────────────────────────────────┤                          │
│  │  id          INTEGER   PK        │                          │
│  │  session_id  INTEGER   FK ───────────► chat_sessions.id     │
│  │  role        STRING              │  "user" or "assistant"   │
│  │  content     TEXT                │                          │
│  │  timestamp   DATETIME            │                          │
│  └──────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                           NEO4J                                 │
│                       Knowledge Graph                           │
│                                                                 │
│   (:Chunk)                                                      │
│     chunk_id, content, embedding (384-dim vector)              │
│     page_number, content_id                                     │
│                                                                 │
│   (:Entity)                                                     │
│     name, type, description                                     │
│     types: disease / drug / gene / symptom / treatment /        │
│            biomarker / clinical trial / guideline / organ ...   │
│                                                                 │
│   [:RELATIONSHIP]                                               │
│     source ──► target                                           │
│     description, strength (1–10)                                │
│                                                                 │
│   (:Chunk) ──[:CONTAINS]──► (:Entity)                          │
│   (:Entity) ──[:RELATED]──► (:Entity)                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Flow 1 — Authentication

```
REGISTER
────────
Browser                     FastAPI                      SQLite
   │                           │                            │
   │  POST /api/users          │                            │
   │  { username,email,pass }  │                            │
   │──────────────────────────►│                            │
   │                           │  check email exists?       │
   │                           │───────────────────────────►│
   │                           │◄── exists / not found ─────│
   │                           │                            │
   │                           │  SHA256(password)          │
   │                           │  INSERT user               │
   │                           │───────────────────────────►│
   │                           │◄── user row ───────────────│
   │                           │                            │
   │                           │  sign JWT { user_id }      │
   │◄──────────────────────────│                            │
   │  { access_token, user }   │                            │
   │  saved to localStorage    │                            │


EVERY PROTECTED REQUEST
───────────────────────
Browser                FastAPI  (api/dependencies.py)
   │                          │
   │  Authorization:          │
   │  Bearer <token>          │
   │─────────────────────────►│
   │                          │  HTTPBearer extracts token
   │                          │  decode_token() → user_id
   │                          │  injected into route handler
```

---

## Flow 2 — Chat (the main flow)

```
User types message → hits Send

Browser              FastAPI /api/chat          SQLite       Neo4j      Azure OpenAI
   │                       │                      │             │              │
   │  POST /api/chat        │                      │             │              │
   │  { query,session_id } │                      │             │              │
   │  Bearer <token>        │                      │             │              │
   │──────────────────────►│                      │             │              │
   │                       │  decode JWT           │             │              │
   │                       │  get user_id          │             │              │
   │                       │                      │             │              │
   │                       │  session_id null?     │             │              │
   │                       │  → CREATE session     │             │              │
   │                       │─────────────────────►│             │              │
   │                       │◄── session.id ────────│             │              │
   │                       │                      │             │              │
   │                       │  SAVE user message    │             │              │
   │                       │─────────────────────►│             │              │
   │                       │                      │             │              │
   │          ┌────────────────── GraphRAG Pipeline ──────────────────────┐   │
   │          │            │                      │             │          │   │
   │          │  Step 1    │  embed query ─────────────────────────────────────►
   │          │            │  ◄── query vector (384-dim) ───────────────────────
   │          │            │                      │             │          │   │
   │          │  Step 2    │  vector search ────────────────────►          │   │
   │          │            │  graph traversal ──────────────────►          │   │
   │          │            │  ◄── chunks + entities + rels ─────           │   │
   │          │            │                      │             │          │   │
   │          │  Step 3    │  fuse into one large context prompt│          │   │
   │          │            │                      │             │          │   │
   │          │  Step 4    │  send to GPT-4o mini ─────────────────────────────►
   │          │            │  ◄── answer ──────────────────────────────────────
   │          └────────────────────────────────────────────────────────────┘   │
   │                       │                      │             │              │
   │                       │  SAVE assistant msg  │             │              │
   │                       │─────────────────────►│             │              │
   │◄──────────────────────│                      │             │              │
   │  { answer, session_id}│                      │             │              │


  ⚠  If Neo4j / LLM is offline:
     → fallback message saved to SQLite instead
     → no crash, user sees a graceful error message
```

---

## Flow 3 — PMC Knowledge Base Ingestion

```
POST /api/ingest/pmc  →  triggers background task

┌──────────────────────────────────────────────────────────────────┐
│                        Background Task                           │
│                                                                  │
│  PMC folders on disk                                             │
│         │                                                        │
│         │  discover_jobs()                                       │
│         ▼                                                        │
│  For each PDF:                                                   │
│         │                                                        │
│         ▼                                                        │
│  pdf_extractor.py  ──────────────────►  raw text per page       │
│         │                                                        │
│         ▼                                                        │
│  text_cleaning.py  ──────────────────►  normalised text         │
│         │                                                        │
│         ▼                                                        │
│  text_chunker.py                                                 │
│    ├── overlapping chunks (1000 chars, 100 overlap)              │
│    └── SentenceTransformer embeddings (384-dim)                  │
│         │                                                        │
│         ▼                                                        │
│  graph_extractor.py  →  GPT-4o mini                             │
│    "Extract entities and relationships from this text"           │
│    ◄── ("entity" METFORMIN | drug | first-line diabetes drug)   │
│    ◄── ("relationship" METFORMIN → TYPE2_DIABETES | treats | 10)│
│         │                                                        │
│         ▼                                                        │
│  neo4j_repository.py                                             │
│    ├── store (:Chunk) nodes with embeddings                      │
│    ├── store (:Entity) nodes                                     │
│    └── store [:RELATIONSHIP] edges                               │
│         │                                                        │
│         ▼                                                        │
│  checkpoint.json  ──  tracks progress, safe to resume on crash  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Flow 4 — Image in Chat (Vision)

```
User attaches image or Ctrl+V pastes screenshot

Browser (client-side)                api/utils/vision.py     Azure OpenAI
   │                                         │                    │
   │  FileReader → base64 dataUrl            │                    │
   │  thumbnail preview shown in input       │                    │
   │  image stored in message on send        │                    │
   │  rendered in chat with lightbox         │                    │
   │                                         │                    │
   │── [TEST] POST /api/vision/test ────────►│                    │
   │           { file: image upload }        │  base64 dataUrl    │
   │                                         │───────────────────►│
   │                                         │◄── text description│
   │◄────────────────────────────────────────│                    │
   │  { description: "ECG showing..." }      │                    │

  ⚠  Image → chat pipeline is UI-complete.
     Next step: send dataUrl to /api/chat,
     prepend GPT-4o description to query before GraphRAG.
```

---

## Flow 5 — PDF Upload + Classification Gate

```
User attaches PDF

                  api/utils/              api/utils/         Azure OpenAI
                  pdf_extractor.py        classifier.py
                        │                     │                   │
PDF bytes ─────────────►│                     │                   │
                        │  PyMuPDF            │                   │
                        │  extract text        │                   │
                        │────────────────────►│                   │
                        │                     │  first 600 words  │
                        │                     │──────────────────►│
                        │                     │◄── JSON result ───│
                        │                     │                   │
                        │  { is_medical: true,│                   │
                        │    confidence: high }│                   │
                        │          │           │                   │
                        │     ┌────┴────┐      │                   │
                        │  YES│         │NO    │                   │
                        │  +high        │or medium/low             │
                        │     ▼         ▼                         │
                        │  Ingest    Skip Neo4j                   │
                        │  into      use as                       │
                        │  Neo4j     context only                 │
                        │  pipeline                               │

  RULE: is_medical=true AND confidence=high  →  Ingest into Neo4j
        anything else                         →  Skip Neo4j

  ⚠  Gate is tested at /api/pdf/test.
     Wiring into /api/chat is the next step.
```

---

## Security Model

```
┌──────────────────────────────────────────────────────────────────┐
│                        SECURITY LAYERS                           │
│                                                                  │
│  1. PASSWORD STORAGE                                             │
│                                                                  │
│     plain password ──► SHA256 (hashlib) ──► stored hash         │
│     never stored plain  ·  never sent after login               │
│                                                                  │
│  2. JWT TOKEN                                                    │
│                                                                  │
│     { user_id } ──► HS256 signed (python-jose) ──► access_token │
│     stored in localStorage                                       │
│     sent as:  Authorization: Bearer <token>                      │
│                                                                  │
│  3. ROUTE PROTECTION                                             │
│                                                                  │
│     HTTPBearer ──► decode_token() ──► user_id                   │
│     every /api/sessions and /api/chat route is guarded           │
│                                                                  │
│  4. SESSION ISOLATION                                            │
│                                                                  │
│     session.user_id != requesting user_id  ──►  403             │
│     frontend catches err.status === 403    ──►  redirect /403   │
│                                                                  │
│  5. CORS                                                         │
│                                                                  │
│     allow_origins: ["*"]   ◄─── open (dev only)                 │
│     restrict before going to production                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

```
AUTH
  POST  /api/users              register new user
  POST  /api/login              login → returns JWT

SESSIONS  (all require Bearer token)
  GET   /api/sessions           list this user's sessions
  POST  /api/sessions           create new session
  PATCH /api/sessions/:id       rename session
  DELETE/api/sessions/:id       delete session
  GET   /api/sessions/:id/messages   get all messages in session

CHAT  (requires Bearer token)
  POST  /api/chat               send query → get AI response

INGESTION
  POST  /api/ingest/pmc         start background PMC ingestion
  GET   /api/ingest/pmc/status  check ingestion progress

VISION (test only — no auth)
  POST  /api/vision/test        upload image → get text description
  POST  /api/pdf/test           upload PDF  → extracted text + classification

HEALTH
  GET   /api/health             health check
```

---

## Tech Stack

```
FRONTEND
  React 18          component UI
  Vite              dev server + build + proxy /api → :8000
  Tailwind CSS      styling
  shadcn/ui         component library (Radix UI primitives)
  React Router v6   client-side routing

BACKEND
  FastAPI           REST API + background tasks
  Uvicorn           ASGI server
  SQLAlchemy async  ORM for SQLite
  aiosqlite         async SQLite driver
  python-jose       JWT signing (HS256)
  python-multipart  file upload support

DATABASES
  SQLite            users, sessions, messages  (medical_rag.db)
  Neo4j             knowledge graph  (bolt://localhost:7687)

AI / ML
  Azure OpenAI      GPT-4o mini  →  chat, extraction, vision, classification
  sentence-transformers  local embeddings (all-MiniLM-L6-v2, 384-dim)

PDF
  PyMuPDF (fitz)    PDF text extraction  (already in requirements)
```

---

## Feature Status

```
✅  WORKING
    Auth (register, login, JWT, session isolation)
    Chat with GraphRAG pipeline
    Neo4j offline fallback (saves message, graceful error)
    Session CRUD (create, list, rename, delete)
    PMC knowledge base ingestion with checkpoint resume
    Dark mode — global, cross-tab sync
    Language (en / ur) — global, cross-tab sync
    Image attach with lightbox + Ctrl+V paste
    POST /api/vision/test  (image file upload → text description)
    POST /api/pdf/test     (PDF file upload → text + classification)
    Medical classification gate (high confidence only → Neo4j)

⚠   BUILT BUT NOT WIRED INTO CHAT YET
    Image → vision → context prepended in /api/chat
    PDF → extraction → classification gate → ingest or context in /api/chat

🔲  DEFINED BUT UNUSED  (dead columns / dead code)
    OAuth login    (oauth_provider, oauth_id, auth_type columns in DB)
    Bookmarks      (UI button works, nothing saves to DB — lost on refresh)
    Source nodes   (GraphRAG finds them, always returned as empty [])
    SessionDetail  (schema exists, no route returns it)
    updated_at     (no column on sessions — can't sort by last active)
    Old ingest route (fully commented out in ingest.py)
```

---

## Directory Map

```
EBM-Connection/
│
├── main_api.py                    FastAPI app entry + router registration
├── config.py                      Pydantic settings (.env loader)
├── requirements.txt
├── .env                           secrets (Azure, Neo4j keys)
├── medical_rag.db                 SQLite database
├── ARCHITECTURE.md                this file
│
├── api/
│   ├── database.py                async SQLAlchemy engine
│   ├── models.py                  ORM models: User, Session, Message
│   ├── schemas.py                 Pydantic request/response types
│   ├── dependencies.py            JWT auth guard (get_current_user)
│   │
│   ├── routes/
│   │   ├── auth.py                POST /users  POST /login
│   │   ├── chat.py                sessions + /chat
│   │   ├── ingest.py              PMC ingestion endpoints
│   │   ├── vision.py              vision + pdf test endpoints
│   │   └── health.py              GET /health
│   │
│   ├── services/
│   │   ├── registry.py            auth business logic
│   │   ├── graph_rag_service.py   4-step GraphRAG pipeline
│   │   ├── pmc_ingestion_service.py  batch PMC ingestion
│   │   ├── pdf_processing_service.py PDF → chunks → Neo4j
│   │   ├── graph_extractor.py     LLM entity/relationship extraction
│   │   ├── text_chunker.py        chunking + embeddings
│   │   ├── pdf_extractor.py       PMC PDF → raw text
│   │   └── prompts.py             LLM prompt templates
│   │
│   ├── repositories/
│   │   ├── chat_history_repo.py   SQLite: users, sessions, messages
│   │   └── neo4j_repsitory.py     Neo4j: store + vector search
│   │
│   └── utils/
│       ├── security.py            SHA256 hash, JWT encode/decode
│       ├── vision.py              image base64 → text description
│       ├── classifier.py          text → medical classification
│       ├── pdf_extractor.py       PDF bytes → plain text (PyMuPDF)
│       ├── parse_plaintext.py     parse LLM entity output
│       └── text_cleaning.py       text normalisation
│
└── Chat-Design/EBM Frontend/
    ├── vite.config.js             proxy: /api → localhost:8000
    └── src/
        ├── App.jsx                router + providers
        ├── pages/                 route-level pages
        ├── components/            shared UI components
        ├── hooks/                 use-auth, use-dark-mode, use-language
        └── api/chatApi.js         all fetch calls + Bearer token
```
