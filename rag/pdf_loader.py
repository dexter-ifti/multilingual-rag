from pathlib import Path

import pymupdf

from rag.models import PDFPage


def load_pdf(pdf_path: str | Path) -> list[PDFPage]:
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = []

    with pymupdf.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            pages.append(
                PDFPage(
                    file_name=pdf_path.name,
                    page_number=page_number,
                    text=text,
                )
            )

    return pages