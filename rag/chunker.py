import re
import uuid

from rag.models import DocumentChunk, PDFPage


def create_chunk_id(
    document_id: str,
    page_number: int,
    chunk_index: int,
) -> str:
    value = f"{document_id}:{page_number}:{chunk_index}"
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            value,
        )
    )

def split_into_paragraphs(text:str)-> list[str]:
    paragraphs = re.split(
        r"\n\s*\n",
        text,
    )
    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]

def chunk_pages(
    pages:list[PDFPage],
    document_id: str,
    chunk_size: int=1500,
) -> list[DocumentChunk]:
    chunks = []

    for page in pages:
        if not page.text.strip():
            continue

        paragraphs = split_into_paragraphs(
            page.text
        )
        
        current_chunk = []
        current_length = 0
        chunk_index = 0

        for paragraph in paragraphs:
            paragraph_length = len(paragraph)
            if (
                current_chunk
                and current_length + paragraph_length
                > chunk_size
            ):
                text = "\n\n".join(
                    current_chunk
                )

                chunks.append(
                    DocumentChunk(
                        chunk_id=create_chunk_id(
                            document_id,
                            page_number=page.page_number,
                            chunk_index=chunk_index
                        ),
                        document_id=document_id,
                        text= text,
                        file_name = page.file_name,
                        page_number = page.page_number,
                        chunk_index=chunk_index
                    )
                )
                chunk_index += 1
                current_chunk = []
                current_length = 0
                
            current_chunk.append(paragraph)
            current_length += paragraph_length

        #  last chunk on page
        if current_chunk:
            text ="\n\n".join(
                current_chunk
            )

            chunks.append(
                DocumentChunk(
                    chunk_id=create_chunk_id(
                        document_id,
                        page.page_number,
                        chunk_index,
                    ),
                    document_id=document_id,
                    text=text,
                    file_name=page.file_name,
                    page_number=page.page_number,
                    chunk_index=chunk_index,
                )
            )
    return chunks