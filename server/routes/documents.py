from pathlib import Path
from uuid import uuid4

import pymupdf
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse

from rag.document_registry import DocumentRegistry
from rag.embeddings import OpenAIEmbeddingProvider
from rag.ingestion import DocumentIngester
from rag.models import DocumentInfo
from rag.vector_store import VectorStore

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


DOCUMENTS_DIR = Path(
    "data/documents"
)

DOCUMENTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_PAGES = 100


registry = DocumentRegistry()

embedding_provider = (
    OpenAIEmbeddingProvider()
)

vector_store = VectorStore()

ingester = DocumentIngester(
    vector_store=vector_store,
    embedding_provider=embedding_provider,
)


@router.post("/upload")
async def upload_documents(
    files: list[UploadFile],
):

    uploaded = []

    for file in files:

        if not file.filename:
            continue

        if not file.filename.lower().endswith(
            ".pdf"
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"{file.filename} "
                    "is not a PDF."
                ),
            )

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"{file.filename} exceeds "
                    "the 10 MB limit."
                ),
            )

        document_id = str(uuid4())

        stored_file_name = (
            f"{document_id}.pdf"
        )

        file_path = (
            DOCUMENTS_DIR
            / stored_file_name
        )

        file_path.write_bytes(content)

        try:

            with pymupdf.open(file_path) as doc:
                page_count = len(doc)

        except Exception:

            file_path.unlink(
                missing_ok=True
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    f"{file.filename} "
                    "is not a valid PDF."
                ),
            )

        if page_count > MAX_PAGES:

            file_path.unlink(
                missing_ok=True
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    f"{file.filename} exceeds "
                    "the 100 page limit."
                ),
            )

        document = DocumentInfo(
            document_id=document_id,
            file_name=file.filename,
            stored_file_name=stored_file_name,
            page_count=page_count,
        )

        registry.add(document)

        ingester.ingest(
            pdf_path=str(file_path),
            document_id=document_id,
        )

        uploaded.append(
            {
                "document_id": document_id,
                "file_name": file.filename,
                "page_count": page_count,
            }
        )

    return {
        "documents": uploaded,
    }


@router.get("")
def list_documents():

    return {
        "documents": [
            {
                "document_id": document.document_id,
                "file_name": document.file_name,
                "page_count": document.page_count,
            }
            for document in registry.list()
        ]
    }


@router.get("/{document_id}/file")
def get_document_file(
    document_id: str,
):

    document = registry.get(
        document_id
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    path = (
        DOCUMENTS_DIR
        / document.stored_file_name
    )

    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail="PDF file not found",
        )

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=document.file_name,
    )