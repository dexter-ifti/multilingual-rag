import json
from pathlib import Path

from rag.models import DocumentInfo


class DocumentRegistry:

    def __init__(
        self,
        path: str = "data/documents.json",
    ):
        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.path.exists():
            self.path.write_text(
                "[]",
                encoding="utf-8",
            )

    def _load(self) -> list[dict]:
        return json.loads(
            self.path.read_text(
                encoding="utf-8"
            )
        )

    def _save(
        self,
        documents: list[dict],
    ) -> None:
        self.path.write_text(
            json.dumps(
                documents,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def add(
        self,
        document: DocumentInfo,
    ) -> None:

        documents = self._load()

        documents.append(
            {
                "document_id": document.document_id,
                "file_name": document.file_name,
                "stored_file_name": document.stored_file_name,
                "page_count": document.page_count,
            }
        )

        self._save(documents)

    def get(
        self,
        document_id: str,
    ) -> DocumentInfo | None:

        documents = self._load()

        for document in documents:

            if document["document_id"] == document_id:

                return DocumentInfo(
                    **document
                )

        return None

    def list(self) -> list[DocumentInfo]:

        return [
            DocumentInfo(**document)
            for document in self._load()
        ]