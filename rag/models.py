from dataclasses import dataclass


@dataclass
class PDFPage:
    file_name: str
    page_number: int
    text: str

@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    text: str 
    file_name: str
    page_number: int
    chunk_index: int
    language: str | None=None

@dataclass
class DocumentInfo:
    document_id: str
    file_name: str
    stored_file_name: str
    page_count: int