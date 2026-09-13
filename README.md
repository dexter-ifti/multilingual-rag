Absolutely. Here’s the **architecture diagram for the current MVP**, with the RAG pipeline, backend, storage, and frontend separated clearly.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MULTILINGUAL DOCUMENT QA                            │
└─────────────────────────────────────────────────────────────────────────────┘


                              USER / BROWSER
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         React + Vite Frontend                               │
│                                                                             │
│   ┌──────────────────┐       ┌──────────────────┐                           │
│   │  PDF Upload UI   │       │    Chat UI       │                           │
│   └────────┬─────────┘       └────────┬─────────┘                           │
│            │                          │                                     │
│            │                          │                                     │
│   ┌────────▼─────────┐       ┌────────▼─────────┐                           │
│   │ Document Sidebar │       │  Source Cards    │                           │
│   └──────────────────┘       │ Open / Translate │                           │
│                              └──────────────────┘                           │
│                                         │                                   │
└─────────────────────────────────────────┼───────────────────────────────────┘
                                          │ HTTP / REST
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FastAPI SERVER                                 │
│                                                                             │
│   POST /documents/upload                                                    │
│   GET  /documents                                                           │
│   GET  /documents/{id}/file                                                 │
│   GET  /documents/{id}/pages/{page}                                         │
│   POST /documents/{id}/pages/{page}/translate                               │
│   POST /chat                                                                │
│                                                                             │
│                         ┌─────────────────────┐                             │
│                         │    API Routes       │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                        │
│                 ┌──────────────────┼───────────────────┐                    │
│                 │                  │                   │                    │
│                 ▼                  ▼                   ▼                    │
│          Document Service     RAG Service       Page Service                │
│                 │                  │                   │                    │
└─────────────────┼──────────────────┼───────────────────┼────────────────────┘
                  │                  │                   │
                  │                  │                   │
                  ▼                  ▼                   ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────────┐
│    DOCUMENT STORE    │  │      RAG PIPELINE    │  │      PAGE SERVICE      │
│                      │  │                      │  │                        │
│  UUID.pdf            │  │  English Question    │  │  document_id           │
│                      │  │          │           │  │       │                │
│  documents.json      │  │          ▼           │  │       ▼                │
│                      │  │  Query Embedding     │  │   PDF File             │
│  document metadata   │  │          │           │  │       │                │
│  - document_id       │  │          ▼           │  │       ▼                │
│  - file_name         │  │      Qdrant          │  │  Page Extraction       │
│  - stored_file_name  │  │          │           │  │       │                │
│  - page_count        │  │          ▼           │  │       ▼                │
│                      │  │   Relevant Chunks    │  │   Page Text             │
└──────────┬───────────┘  │          │           │  │       │                │
           │              │          ▼           │  │       ▼                │
           │              │    OpenAI LLM        │  │ OpenAI Translator      │
           │              │          │           │  │       │                │
           │              │     ┌────┴────┐      │  │       ▼                │
           │              │     ▼         ▼      │  │ English Translation    │
           │              │  Answer    Sources   │  │                        │
           │              └──────────────────────┘  └────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              QDRANT CLOUD                                    │
│                                                                             │
│  Collection: Documents                                                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Vector                                                              │    │
│  │                                                                     │    │
│  │ Payload                                                             │    │
│  │ ├── document_id                                                     │    │
│  │ ├── file_name                                                       │    │
│  │ ├── page_number                                                     │    │
│  │ ├── chunk_index                                                      │    │
│  │ ├── language                                                         │    │
│  │ └── text                                                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


                         INGESTION FLOW
                         ══════════════

        PDF
         │
         ▼
   Validate PDF
   ├── <= 10 MB
   └── <= 100 pages
         │
         ▼
   Generate document_id
         │
         ├──────────────────────► Save UUID.pdf
         │
         ▼
     PyMuPDF
         │
         ▼
   Extract page text
         │
         ▼
   Paragraph-aware chunking
         │
         ▼
   OpenAI Embeddings
         │
         ▼
      Qdrant
         │
         ▼
    Ready to query


                         QUERY FLOW
                         ═══════════

 English Question
        │
        ▼
     FastAPI
        │
        ▼
 OpenAI Embedding
        │
        ▼
     Qdrant
        │
        ▼
 Top-K relevant chunks
        │
        ▼
     Context
        │
        ▼
    OpenAI LLM
        │
        ├───────────────► English Answer
        │
        └───────────────► Source Metadata
                                │
                                ├── document_id
                                ├── file_name
                                └── page_number


                       SOURCE INTERACTION
                       ═══════════════════

       Source Card
           │
           ├──────────────────────────────┐
           │                              │
           ▼                              ▼
        [ OPEN ]                     [ TRANSLATE ]
           │                              │
           ▼                              ▼
 /documents/{id}/file          /documents/{id}/pages/{page}
           │                              │
       #page=N                             ▼
           │                       Extract full page
           ▼                              │
     Browser PDF                          ▼
     viewer                         OpenAI Translation
                                          │
                                          ▼
                                  Original + English
                                  Translation Panel
```

### The key architectural boundary

The most important design decision is this:

```text
                    ┌────────────────────┐
                    │     FRONTEND       │
                    │                    │
                    │  UI only           │
                    └─────────┬──────────┘
                              │
                              │ REST API
                              ▼
                    ┌────────────────────┐
                    │      FASTAPI       │
                    │                    │
                    │ API orchestration  │
                    └─────────┬──────────┘
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
          ┌────────┐      ┌────────┐      ┌──────────┐
          │  RAG   │      │ Pages  │      │Documents │
          │ Core   │      │        │      │          │
          └───┬────┘      └───┬────┘      └────┬─────┘
              │                │                │
              ▼                ▼                ▼
           Qdrant           OpenAI          PDF Store
```

That means later, when we improve retrieval, **the frontend doesn't need to change**.

And when we add OCR:

```text
PyMuPDF ──────► text PDF
    │
    └──────────► OCR ──────► scanned PDF
```

we can modify the ingestion layer without redesigning the API or UI.

### Current vs future

```text
CURRENT MVP                         FUTURE
─────────────                       ──────

PyMuPDF                             PyMuPDF + OCR
     │                                    │
     ▼                                    ▼
Chunks                              Language detection
     │                                    │
     ▼                                    ▼
Embeddings                          Better chunking
     │                                    │
     ▼                                    ▼
Qdrant                              Hybrid retrieval
     │                                    │
     ▼                                    ▼
Top-K                               Reranking
     │                                    │
     ▼                                    ▼
LLM                                 Evidence selection
     │                                    │
     ▼                                    ▼
Answer + sources                    Verified citations
```

**This is the diagram I'd put in your project README/project presentation.**
