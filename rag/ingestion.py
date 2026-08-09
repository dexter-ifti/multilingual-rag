from rag.chunker import chunk_pages
from rag.embeddings import OpenAIEmbeddingProvider
from rag.pdf_loader import load_pdf
from rag.vector_store import VectorStore


class DocumentIngester:

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_provider: OpenAIEmbeddingProvider,
    ):
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider

    def ingest(self, pdf_path: str, document_id: str) -> str:

        print(f"Loading: {pdf_path}")


        pages = load_pdf(pdf_path)

        print(f"Pages: {len(pages)}")

        chunks = chunk_pages(pages, document_id=document_id)

        print(f"Chunks: {len(chunks)}")

        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_provider
            .embed_documents(texts)
        )

        print("Embeddings created")

        self.vector_store.add_chunks(
            chunks,
            embeddings,
        )

        print("Stored in Qdrant")

        print(
            f"Document ID: {document_id}"
        )

        return document_id