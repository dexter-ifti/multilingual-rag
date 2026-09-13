# Multilingual Document QA — Project Context / Handoff

## 1. Project

Challenge: Multilingual Document QA with Source Linking.

Goal:
- Users upload multiple PDFs, potentially in Indian vernacular languages.
- Maximum 10 MB per PDF.
- Maximum 100 pages per PDF.
- Users ask questions in English.
- RAG retrieves relevant passages from uploaded PDFs.
- LLM answers in English.
- Answers show source file name and page number.
- Clicking a source opens the original PDF at the cited page.
- User can translate the selected PDF page into English.

Current stack:
- Python 3.12
- `uv`
- PyMuPDF
- OpenAI API
- Qdrant Cloud
- FastAPI
- React + Vite + TypeScript
- Axios
- Plain CSS for frontend

OCR is intentionally postponed. We will add it later for scanned PDFs.

---

## 2. Current architecture

```text
                         PDF UPLOAD
                             |
                             v
                       FastAPI server
                             |
                   validate PDF / limits
                             |
                             v
                    document_id generated
                             |
              +--------------+--------------+
              |                             |
              v                             v
        Save original PDF              RAG ingestion
                                            |
                                            v
                                      PyMuPDF extraction
                                            |
                                            v
                                      page-aware chunks
                                            |
                                            v
                                      OpenAI embeddings
                                            |
                                            v
                                          Qdrant


English question
       |
       v
   FastAPI /chat
       |
       v
question embedding
       |
       v
     Qdrant
       |
       v
relevant chunks
       |
       v
   OpenAI LLM
       |
       +------------------+
       |                  |
       v                  v
     answer            sources
                           |
                           +--> document_id
                           +--> file_name
                           +--> page_number


Source "Open"
       |
       v
GET /documents/{document_id}/file#page=N
       |
       v
browser PDF viewer


Source "Translate"
       |
       v
POST /documents/{document_id}/pages/{page}/translate
       |
       v
extract actual PDF page
       |
       v
OpenAI translation
       |
       v
original text + English translation
```

---

## 3. Project structure

Current/target structure:

```text
06-multilingual-rag/
|
├── data/
│   ├── documents/
│   └── documents.json
|
├── rag/
│   ├── __init__.py
│   ├── models.py
│   ├── pdf_loader.py
│   ├── ocr.py                 # future; currently skipped
│   ├── language.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── documents.py
│   ├── document_registry.py
│   ├── ingestion.py
│   ├── generator.py
│   ├── qa.py
│   ├── page_service.py
│   └── translator.py
|
├── scripts/
│   ├── ingest.py
│   ├── ask.py
│   ├── test_loader.py
│   ├── test_embeddings.py
│   ├── test_qdrant.py
│   ├── test_rag_retrieval.py
│   └── test_translation.py
|
├── server/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── documents.py
│   │   └── pages.py
│   └── services/
│       ├── __init__.py
│       └── rag_service.py
|
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   ├── UploadZone.tsx
│   │   │   ├── Chat.tsx
│   │   │   ├── SourceCard.tsx
│   │   │   └── TranslationPanel.tsx
│   │   ├── types/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── main.tsx
│   └── ...
|
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## 4. PDF extraction

PyMuPDF is used for PDF extraction.

Important historical issue:
- Initially `import fitz` imported the wrong `fitz` package / namespace.
- `uv add pymupdf` was performed.
- Environment/package state was cleaned until PyMuPDF imported correctly.
- Current implementation can use either the project convention already established (`fitz`) or preferably `import pymupdf` if code has been migrated to the newer namespace.
- Do not reintroduce the unrelated `fitz` package.

The PDF loader already successfully produced:
- total pages
- character count per page
- total pages
- empty pages
- page-level text

One test PDF:
- `vardan.pdf`
- 47 pages
- 71 chunks

---

## 5. Chunking

Current approach:
- Paragraph-aware splitting.
- Page metadata is preserved.
- Each chunk has:
  - chunk ID
  - document ID
  - file name
  - page number
  - chunk index
  - text
  - optional language

We intentionally chose paragraph-wise splitting because it is better for conversational/prose documents than blindly splitting every N characters.

Do NOT aggressively optimize chunking yet.

---

## 6. Embeddings

OpenAI embeddings are already working.

A multilingual test was successful.

Example test similarity output included Hindi text such as:

```text
0.1419  किसानों को इस योजना के तहत आर्थिक सहायता प्रदान की जाती है।
0.1184  भारत में कई प्रकार की फसलें उगाई जाती हैं।
0.0233  दिल्ली भारत की राजधानी है।
```

The exact embedding model/config is already in `rag/embeddings.py`; preserve the existing implementation rather than replacing it unnecessarily.

The user has OpenAI API credits and does not have a powerful local machine, so cloud embeddings/LLM are preferred.

---

## 7. Qdrant

Qdrant Cloud is currently being used.

The user also wanted to understand local Qdrant, but the working project currently uses their cloud URL/API key.

A Qdrant collection named:

```text
Documents
```

was successfully created.

Important Qdrant issue encountered:
- First upsert timed out while uploading too much data in one request.
- Then Qdrant returned:
  `400 ... value fd82228c4599050e is not a valid point ID`
- Cause: chunk IDs were strings that were not valid Qdrant IDs.
- Fix: chunk IDs were changed to UUIDs.

Current chunk IDs should therefore be valid UUIDs or unsigned integers.

Qdrant payload now includes:

```text
document_id
text
file_name
page_number
chunk_index
language
```

---

## 8. Document identity

This is important.

The project now uses `document_id` as the canonical document identifier.

Do NOT use filename as the primary identity.

Reason:
Two different users/documents can both upload:

```text
report.pdf
```

The backend stores PDFs using a unique generated ID, conceptually:

```text
document_id = UUID

stored file:
{document_id}.pdf
```

Registry metadata looks like:

```json
{
  "document_id": "uuid",
  "file_name": "vardan.pdf",
  "stored_file_name": "uuid.pdf",
  "page_count": 47
}
```

A simple JSON document registry is currently used for the MVP:

```text
data/documents.json
```

Do not introduce PostgreSQL yet unless needed. The JSON registry is adequate for the current local MVP.

---

## 9. RAG pipeline

The intended separation is:

### Ingestion

```text
PDF
 -> load
 -> chunks
 -> embeddings
 -> Qdrant
```

This happens once per document.

### Query

```text
English question
 -> question embedding
 -> Qdrant retrieval
 -> LLM
 -> answer + source metadata
```

Do NOT re-embed the whole PDF every time a user asks a question.

---

## 10. RAG answer generation

`rag/generator.py` uses the OpenAI Responses API.

The generator instructions tell the model:
- answer in English
- context may be in Hindi/Tamil/Bengali/etc.
- use only supplied context
- don't use outside knowledge
- don't invent facts
- if context is insufficient, say:
  "I couldn't find enough information in the uploaded documents."
- don't expose implementation details such as embeddings/Qdrant.

The current RAG output is structured approximately as:

```python
QAResponse(
    answer="...",
    sources=[
        Source(
            document_id="...",
            file_name="vardan.pdf",
            page_number=35,
            chunk_index=0,
            score=0.61,
        )
    ],
)
```

---

## 11. Retrieval caveat / postponed improvement

A retrieval test was run against Premchand's `Vardan`.

A question like:

```text
What is this book about?
```

returned several semantically similar passages.

Later tests showed that a specific relevant page might be ranked third rather than first, e.g.:

```text
43, 16, 35
```

The user correctly observed that this may happen because:
- `Vardan` is literary prose
- many scenes contain recurring characters
- conversations between Pratap and Virjan can be semantically similar
- raw vector similarity does not necessarily mean "best citation"

IMPORTANT:
This is intentionally NOT being optimized yet.

We agreed:
1. Finish the application.
2. Test with better/more varied PDFs.
3. Then improve retrieval/citations.

Future retrieval improvements may include:
- reranking
- page grouping
- deduplicating same-page chunks
- evidence selection
- citation validation
- hybrid retrieval
- metadata filtering
- better evaluation datasets

Current top-k retrieval results should be treated as candidate evidence, not perfectly verified citations.

---

## 12. Current RAG source deduplication

Sources should eventually be deduplicated by:

```text
(document_id, page_number)
```

so multiple chunks from the same page do not produce repeated UI sources.

The UI should show something like:

```text
Sources

vardan.pdf — Page 35
vardan.pdf — Page 34
```

not:

```text
vardan.pdf — Page 35 chunk 0
vardan.pdf — Page 35 chunk 1
vardan.pdf — Page 35 chunk 2
```

---

## 13. Translation

OCR is intentionally skipped for now.

Current translation flow:

```text
source click
 -> document_id
 -> page_number
 -> extract actual PDF page
 -> translate entire page to English
```

This is intentionally page-level translation, NOT chunk-level translation.

Why:
The challenge says clicking a source should open the PDF page and allow English translation.

`rag/page_service.py` resolves the PDF by `document_id`, then extracts:

```python
page = doc[page_number - 1]
page.get_text("text")
```

User-visible page numbering starts at 1; PyMuPDF indexes from 0.

`rag/translator.py` uses OpenAI and asks for:
- natural English translation
- preserve meaning
- do not summarize
- don't add information
- preserve names/places
- preserve paragraph structure where possible
- return only translation

Future improvement:
- cache translation by `(document_id, page_number)` to avoid paying for repeated translations.

---

## 14. FastAPI backend

FastAPI is working.

Current endpoints:

```text
GET  /health

POST /documents/upload
GET  /documents
GET  /documents/{document_id}/file

GET  /documents/{document_id}/pages/{page_number}
POST /documents/{document_id}/pages/{page_number}/translate

POST /chat
```

### Upload

Requirements enforced:
- PDF only
- max 10 MB
- max 100 pages

Upload accepts multiple files.

Current upload flow:

```text
POST /documents/upload
 -> validate
 -> generate document_id
 -> save PDF as UUID.pdf
 -> count pages
 -> register document
 -> ingest into Qdrant
 -> return document metadata
```

Current response is approximately:

```json
{
  "documents": [
    {
      "document_id": "...",
      "file_name": "vardan.pdf",
      "page_count": 47
    }
  ]
}
```

Note:
Current upload performs ingestion synchronously. This is okay for the MVP.

Future improvement:
Use background processing:

```text
upload
 -> 202
 -> processing
 -> ready
```

Do this after the main UI works.

---

## 15. PDF file endpoint

The frontend can open:

```text
/documents/{document_id}/file#page=35
```

The backend returns the original PDF.

This lets the browser's PDF viewer jump to the cited page.

---

## 16. Page endpoints

Get original page text:

```text
GET /documents/{document_id}/pages/{page_number}
```

Response:

```json
{
  "document_id": "...",
  "page_number": 35,
  "text": "..."
}
```

Translate page:

```text
POST /documents/{document_id}/pages/{page_number}/translate
```

Response:

```json
{
  "document_id": "...",
  "page_number": 35,
  "original_text": "...",
  "translation": "..."
}
```

---

## 17. Chat endpoint

Request:

```json
{
  "question": "What does Pratap say to Virjan?"
}
```

Response should be approximately:

```json
{
  "answer": "...",
  "sources": [
    {
      "document_id": "...",
      "file_name": "vardan.pdf",
      "page_number": 35
    }
  ]
}
```

Retrieval score is an internal detail and should ideally not be exposed in the final UI.

---

## 18. CORS

Frontend and backend are on different origins:

```text
http://localhost:5173
http://localhost:8000
```

This caused a CORS error during PDF upload.

Fixed by adding FastAPI/Starlette CORSMiddleware.

Current development configuration should allow:

```python
allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

with:

```python
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

The CORS issue is resolved and upload is working.

Do not remove the middleware.

---

## 19. Frontend

Frontend was created with:

```text
React + Vite + TypeScript
```

Axios is installed.

Frontend structure:

```text
frontend/src/
├── api/
│   └── client.ts
├── components/
│   ├── UploadZone.tsx
│   ├── Chat.tsx
│   ├── SourceCard.tsx
│   └── TranslationPanel.tsx
├── types/
│   └── api.ts
├── App.tsx
├── App.css
└── main.tsx
```

---

## 20. Frontend API types

Current types are approximately:

```typescript
export interface Document {
  document_id: string;
  file_name: string;
  page_count: number;
}

export interface Source {
  document_id: string;
  file_name: string;
  page_number: number;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
}

export interface PageResponse {
  document_id: string;
  page_number: number;
  text: string;
}

export interface TranslationResponse {
  document_id: string;
  page_number: number;
  original_text: string;
  translation: string;
}
```

---

## 21. Frontend API client

`frontend/src/api/client.ts` contains functions roughly:

```typescript
getDocuments()
uploadDocuments(files)
askQuestion(question)
getPage(documentId, pageNumber)
translatePage(documentId, pageNumber)
getPdfUrl(documentId)
```

Backend base URL is currently:

```text
http://localhost:8000
```

---

## 22. Frontend UI currently working

The UI has:
- document sidebar
- upload button
- PDF upload
- document list
- chat interface
- user messages
- assistant answers
- source cards
- Open source button
- Translate source button
- translation side panel

The basic version is visible and working.

The user confirmed:
- basic frontend works
- PDF upload works after CORS fix
- backend routes work
- chat looks good
- translation/source interaction is being implemented

---

## 23. Current frontend UX

Conceptually:

```text
┌─────────────────────────────────────────────────────────────┐
│ Document QA                                                 │
│ Ask questions across multilingual PDFs                     │
├──────────────────────┬──────────────────────────────────────┤
│ DOCUMENTS            │                                      │
│                      │ You                                  │
│ [+ Upload PDFs]      │ What does Pratap say to Virjan?      │
│                      │                                      │
│ 📄 vardan.pdf        │ AI                                   │
│    47 pages          │ Pratap tells Virjan...               │
│                      │                                      │
│ 📄 another.pdf       │ Sources                              │
│    20 pages          │ ┌──────────────────────────────────┐ │
│                      │ │ 📄 vardan.pdf       [Open]       │ │
│                      │ │ Page 35             [Translate]  │ │
│                      │ └──────────────────────────────────┘ │
│                      │                                      │
│                      │ Ask a question...                 ↑  │
└──────────────────────┴──────────────────────────────────────┘
```

Translation panel:

```text
┌────────────────────────────────────┐
│ vardan.pdf                     ×   │
│ Page 35                            │
├────────────────────────────────────┤
│ ORIGINAL                           │
│                                    │
│ Hindi text...                      │
│                                    │
│ ENGLISH                            │
│                                    │
│ English translation...             │
└────────────────────────────────────┘
```

---

## 24. Immediate next tasks

Do these in this order:

### A. Verify source Open

Click Open and verify:

```text
/documents/{document_id}/file#page={page}
```

opens the correct PDF page.

### B. Finish translation panel

Verify:

```text
Translate
 -> POST /documents/{id}/pages/{page}/translate
 -> side panel
 -> original + English
```

### C. Translation cache

Avoid repeatedly paying for the same page translation.

Simple MVP cache options:
- in-memory dictionary
- JSON cache
- later Redis/database

Key:

```text
(document_id, page_number)
```

### D. Improve document upload UX

Currently upload waits for ingestion.

Later:

```text
upload
 -> processing state
 -> ready state
```

### E. Add document selection

Current chat searches all documents.

Future UI:

```text
Ask across all documents

or

[x] vardan.pdf
[ ] tamil_report.pdf
[ ] bengali_policy.pdf
```

Backend can pass a `document_id` filter or multiple document IDs into Qdrant.

### F. Retrieval evaluation

Only after the complete app is working:
- create better test PDFs
- evaluate retrieval
- test top-k
- test reranking
- improve citation accuracy
- group results by page
- test multilingual queries/documents

### G. OCR

Do later.

Expected future flow:

```text
PDF
 |
 +-- has text --> PyMuPDF
 |
 +-- scanned --> OCR
                  |
                  v
                chunks
```

Do not add OCR before the MVP is complete.

---

## 25. Important architectural principles

1. Keep RAG logic outside FastAPI routes.
2. Keep frontend unaware of Qdrant/OpenAI implementation.
3. Use `document_id` as the canonical identity.
4. Preserve file name and page number as metadata for citations.
5. Never re-embed an already-ingested PDF for every question.
6. Do not treat raw top-k vector results as perfectly verified citations.
7. Translation should operate on the full cited page.
8. OCR is intentionally postponed.
9. Don't overengineer the MVP.
10. Finish the browser experience before optimizing retrieval.

---

## 26. Useful commands

### Python environment

```bash
uv sync
```

### Run backend

```bash
uv run uvicorn server.main:app --reload
```

### Run frontend

```bash
cd frontend
npm run dev
```

### Test ingestion

```bash
uv run python -m scripts.ingest data/raw/vardan.pdf
```

Adjust path according to current project layout.

### Test RAG directly

```bash
uv run python -m scripts.ask
```

### Test translation

```bash
uv run python -m scripts.test_translation
```

### Test Qdrant

```bash
uv run python scripts/test_qdrant.py
```

### FastAPI docs

```text
http://localhost:8000/docs
```

### Frontend

```text
http://localhost:5173
```

---

## 27. Current status

```text
RAG extraction             ✅
Paragraph chunking         ✅
Multilingual embeddings    ✅
Qdrant                     ✅
Document IDs               ✅
Multi-PDF ingestion        ✅
English question           ✅
LLM answer                 ✅
Source metadata            ✅
FastAPI                    ✅
PDF validation             ✅
PDF serving                ✅
Page extraction            ✅
Page translation           ✅
React frontend             ✅
Upload UI                  ✅
Chat UI                    ✅
Source UI                  ✅
CORS                       ✅

OCR                        ⏸ Future
Translation cache          ⏳ Next
Background ingestion       ⏳ Later
Document selection         ⏳ Next
Retrieval optimization     ⏳ After MVP
Final polish               ⏳ Later
```

---

## 28. Continuation instruction for a new ChatGPT conversation

Paste this file into the new conversation and say:

> Continue this project from the current state. Do not restart the architecture. Read the project context and help me implement the next task step-by-step. I am using Python, FastAPI, React/Vite/TypeScript, OpenAI, and Qdrant. Keep the implementation practical because my machine is not powerful and I prefer cloud APIs for embeddings/LLM.

The most likely next task is:

> Finish and test the PDF source Open interaction and translation panel, then add translation caching and document selection.

