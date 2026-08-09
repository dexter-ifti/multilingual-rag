from pathlib import Path

import pymupdf

from rag.document_registry import DocumentRegistry


class PageService:

    def __init__(
        self,
        documents_dir: str = "data/documents",
        registry: DocumentRegistry | None = None,
    ):
        self.documents_dir = Path(
            documents_dir
        )

        self.registry = (
            registry
            or DocumentRegistry()
        )

    def _get_pdf_path(
        self,
        document_id: str,
    ) -> Path:

        document = self.registry.get(
            document_id
        )

        if document is None:
            raise FileNotFoundError(
                f"Document not found: {document_id}"
            )

        return (
            self.documents_dir
            / document.stored_file_name
        )

    def get_page_text(
        self,
        document_id: str,
        page_number: int,
    ) -> str:

        pdf_path = self._get_pdf_path(
            document_id
        )

        with pymupdf.open(pdf_path) as doc:

            if (
                page_number < 1
                or page_number > len(doc)
            ):
                raise ValueError(
                    f"Invalid page number: "
                    f"{page_number}"
                )

            page = doc[page_number - 1]

            return page.get_text(
                "text"
            ).strip()