import sys

from dotenv import load_dotenv

from rag.embeddings import OpenAIEmbeddingProvider
from rag.ingestion import DocumentIngester
from rag.vector_store import VectorStore

load_dotenv()

if len(sys.argv) != 2:
    print(
        "Usage: "
        "uv run python -m scripts.ingest <pdf>"
    )
    raise SystemExit(1)


pdf_path = sys.argv[1]


embedding_provider = OpenAIEmbeddingProvider()

vector_store = VectorStore()

ingester = DocumentIngester(
    vector_store=vector_store,
    embedding_provider=embedding_provider,
)

document_id = ingester.ingest(pdf_path)

print(
    f"\nSuccessfully ingested "
    f"document_id: {document_id}."
)